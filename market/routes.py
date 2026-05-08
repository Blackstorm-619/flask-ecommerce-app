from market import app, db, csrf
from flask import render_template, redirect, url_for, flash, request, jsonify
from market.models import Item, User, Review, ProductImage, Order, Cart
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm, ReviewForm, CSRFForm
from flask_login import login_user, logout_user, login_required, current_user
import razorpay, hmac, hashlib, os

# ── HOME ─────────────────────────────────────────────

@app.route('/')
@app.route('/home')
def home_page():
    return render_template(
        'home.html',
        total_items=Item.query.count(),
        total_users=User.query.count(),
        featured_items=Item.query.filter_by(owner=None).limit(8).all(),
        categories=[]
    )


# ── MARKET ───────────────────────────────────────────

@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()

    if request.method == "POST":
        sold_item = request.form.get('sold_item')
        item = Item.query.filter_by(name=sold_item).first()
        if item and current_user.can_sell(item):
            item.sell(current_user)
            flash(f"Sold {item.name} back to market!", "success")
        elif sold_item:
            flash(f"Something went wrong selling {sold_item}.", "danger")
        return redirect(url_for('market_page'))

    return render_template(
        'market.html',
        items=Item.query.filter_by(owner=None),
        owned_items=Item.query.filter_by(owner=current_user.id),
        purchase_form=purchase_form,
        selling_form=selling_form
    )


# ── ITEM DETAIL ──────────────────────────────────────

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)

    has_purchased = False
    in_cart = False

    if current_user.is_authenticated:
        has_purchased = (
            item.owner == current_user.id or
            Order.query.filter_by(user_id=current_user.id, item_id=item_id).first() is not None
        )
        in_cart = Cart.query.filter_by(
            user_id=current_user.id, item_id=item_id
        ).first() is not None

    return render_template(
        'item_detail.html',
        item=item,
        images=ProductImage.query.filter_by(item_id=item_id).all(),
        reviews=Review.query.filter_by(item_id=item_id)
                 .order_by(Review.date_posted.desc()).all(),
        purchase_form=PurchaseItemForm(),
        review_form=ReviewForm(),
        has_purchased=has_purchased,
        in_cart=in_cart,
        csrf_form=CSRFForm()
    )


# ── REVIEWS ──────────────────────────────────────────

@app.route('/item/<int:item_id>/review', methods=['POST'])
@login_required
def add_review(item_id):
    item = Item.query.get_or_404(item_id)

    has_purchased = (
        item.owner == current_user.id or
        Order.query.filter_by(user_id=current_user.id, item_id=item_id).first()
    )
    if not has_purchased:
        flash("You need to purchase this item before leaving a review.", "danger")
        return redirect(url_for('item_detail', item_id=item_id))

    if Review.query.filter_by(user_id=current_user.id, item_id=item_id).first():
        flash("You have already reviewed this item.", "warning")
        return redirect(url_for('item_detail', item_id=item_id))

    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()

    if not rating or not (1 <= rating <= 5):
        flash("Please select a rating between 1 and 5.", "danger")
        return redirect(url_for('item_detail', item_id=item_id))

    if not comment:
        flash("Please write a comment.", "danger")
        return redirect(url_for('item_detail', item_id=item_id))

    db.session.add(Review(
        user_id=current_user.id,
        item_id=item_id,
        rating=rating,
        comment=comment
    ))
    db.session.commit()
    flash("Your review has been posted!", "success")
    return redirect(url_for('item_detail', item_id=item_id))


# ── AUTH ─────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password=form.password1.data
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f"Account created! Welcome, {user.username}", "success")
        return redirect(url_for('market_page'))

    for errors in form.errors.values():
        for err in errors:
            flash(err, "danger")

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password_correction(form.password.data):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for('market_page'))
        flash("Username and password do not match.", "danger")
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('home_page'))


# ── CART ─────────────────────────────────────────────

@app.route('/cart')
@login_required
def cart_page():
    entries = Cart.query.filter_by(user_id=current_user.id).all()

    valid_entries = []
    for entry in entries:
        if entry.item.owner is None:
            valid_entries.append(entry)
        else:
            db.session.delete(entry)
    db.session.commit()

    cart_items = [
        {
            'cart_id': e.id,
            'item':     e.item,
            'quantity': e.quantity,
            'subtotal': e.item.price * e.quantity,
        }
        for e in valid_entries
    ]

    total = sum(i['subtotal'] for i in cart_items)
    return render_template(
        'cart.html',
        cart_items=cart_items,
        total=total,
        can_afford=current_user.budget >= total
    )


@app.route('/cart/add/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    item = Item.query.get_or_404(item_id)

    if item.owner:
        flash(f'"{item.name}" is no longer available.', "danger")
        return redirect(request.referrer or url_for('market_page'))

    quantity = max(1, request.form.get('quantity', 1, type=int))
    existing = Cart.query.filter_by(user_id=current_user.id, item_id=item_id).first()

    if existing:
        existing.quantity += quantity
        flash(f'Updated quantity for "{item.name}".', "info")
    else:
        db.session.add(Cart(user_id=current_user.id, item_id=item_id, quantity=quantity))
        flash(f'"{item.name}" added to cart!', "success")

    db.session.commit()
    return redirect(request.referrer or url_for('market_page'))


@app.route('/cart/remove/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    entry = Cart.query.get_or_404(cart_id)
    if entry.user_id == current_user.id:
        db.session.delete(entry)
        db.session.commit()
        flash("Item removed from cart.", "info")
    return redirect(url_for('cart_page'))


@app.route('/cart/update/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    entry = Cart.query.get_or_404(cart_id)
    if entry.user_id != current_user.id:
        return redirect(url_for('cart_page'))

    quantity = request.form.get('quantity', 1, type=int)
    if quantity < 1:
        db.session.delete(entry)
        flash("Item removed from cart.", "info")
    else:
        entry.quantity = quantity
        flash("Cart updated.", "success")

    db.session.commit()
    return redirect(url_for('cart_page'))


# ── PROFILE & ORDER HISTORY ──────────────────────────

@app.route('/profile')
@login_required
def profile_page():
    orders = Order.query.filter_by(user_id=current_user.id)\
                        .order_by(Order.date_ordered.desc()).all()
    return render_template(
        'profile.html',
        orders=orders,
        total_spent=sum(o.total_price for o in orders),
        total_orders=len(orders),
        owned_count=Item.query.filter_by(owner=current_user.id).count()
    )


@app.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash("You don't have permission to view this order.", "danger")
        return redirect(url_for('profile_page'))
    return render_template('order_detail.html', order=order)


# ── RAZORPAY ─────────────────────────────────────────

razorpay_client = razorpay.Client(
    auth=(os.getenv('RAZORPAY_KEY_ID'), os.getenv('RAZORPAY_KEY_SECRET'))
)


@app.route('/cart/create-order', methods=['POST'])
@csrf.exempt
@login_required
def create_razorpay_order():
    entries = Cart.query.filter_by(user_id=current_user.id).all()

    if not entries:
        return jsonify({'error': 'Cart is empty'}), 400

    total_paise = sum(
        e.item.price * e.quantity * 100
        for e in entries if e.item.owner is None
    )

    if total_paise == 0:
        return jsonify({'error': 'No valid items'}), 400

    order = razorpay_client.order.create({
        'amount': total_paise,
        'currency': 'INR',
        'payment_capture': 1
    })

    return jsonify({
        'order_id': order['id'],
        'amount':   total_paise,
        'key':      app.config['RAZORPAY_KEY_ID'],
        'name':     current_user.username,
        'email':    current_user.email_address
    })


@app.route('/cart/verify-payment', methods=['POST'])
@csrf.exempt
@login_required
def verify_payment():
    data = request.get_json()

    body = data['razorpay_order_id'] + '|' + data['razorpay_payment_id']
    expected = hmac.new(
        app.config['RAZORPAY_KEY_SECRET'].encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    if expected != data['razorpay_signature']:
        return jsonify({'error': 'Invalid signature'}), 400

    entries = Cart.query.filter_by(user_id=current_user.id).all()
    purchased = []

    for entry in entries:
        item = entry.item
        if item.owner is not None:
            db.session.delete(entry)
            continue
        item.owner = current_user.id
        current_user.budget -= item.price * entry.quantity
        db.session.add(Order(
            user_id=current_user.id,
            item_id=item.id,
            quantity=entry.quantity,
            total_price=item.price * entry.quantity,
            status='Completed'
        ))
        db.session.delete(entry)
        purchased.append(item.name)

    db.session.commit()
    return jsonify({'success': True, 'purchased': purchased})