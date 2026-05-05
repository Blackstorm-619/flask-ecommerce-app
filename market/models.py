from market import db, login_manager
from market import bcrypt
from flask_login import UserMixin
import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=100000)
    items = db.relationship('Item', backref='owned_user', lazy=True)
    reviews = db.relationship('Review', backref='reviewer', lazy=True)
    orders = db.relationship('Order', backref='buyer', lazy=True)
    cart_items = db.relationship('Cart', backref='user', lazy=True, cascade='all, delete-orphan')
    cart_entries = db.relationship('Cart', backref='cart_user', lazy=True)

    @property
    def prettier_budget(self):
        if len(str(self.budget)) >= 4:
            return f'₹{str(self.budget)[:-3]},{str(self.budget)[-3:]}'
        else:
            return f"₹{self.budget}"

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def can_purchase(self, item_obj):
        return self.budget >= item_obj.price

    def can_sell(self, item_obj):
        return item_obj in self.items


class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=1024), nullable=False, unique=True)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    stock = db.Column(db.Integer(), nullable=False, default=1)
    # Relationships
    images = db.relationship('ProductImage', backref='item', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='item', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='item', lazy=True)
    cart_entries = db.relationship('Cart', backref='item', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'Item {self.name}'

    def buy(self, user):
        self.owner = user.id
        user.budget -= self.price
        db.session.commit()

    def sell(self, user):
        self.owner = None
        user.budget += self.price
        db.session.commit()


class ProductImage(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    item_id = db.Column(db.Integer(), db.ForeignKey('item.id'), nullable=False)
    image_url = db.Column(db.String(length=200), nullable=False)


class Review(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer(), db.ForeignKey('item.id'), nullable=False)
    rating = db.Column(db.Integer(), nullable=False)  # 1-5
    comment = db.Column(db.String(length=500), nullable=False)
    date_posted = db.Column(db.DateTime(), default=datetime.datetime.utcnow)


class Order(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer(), db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer(), nullable=False, default=1)
    total_price = db.Column(db.Integer(), nullable=False, default=0)
    status = db.Column(db.String(length=20), default='Pending')
    date_ordered = db.Column(db.DateTime(), default=datetime.datetime.utcnow)


class Cart(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer(), db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer(), default=1)
