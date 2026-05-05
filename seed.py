from market import app, db
from market.models import Item

# Run this script once to populate your database with dummy items.
# Usage: python seed.py

items = [
    # Electronics
    Item(name="Wireless Earbuds",     price=2999,  barcode="100000000001", stock=15,
         description="Compact wireless earbuds with active noise cancellation, 24hr battery life, and IPX5 water resistance. Perfect for workouts and commutes."),

    Item(name="Mechanical Keyboard", price=4499,  barcode="100000000002", stock=8,
         description="TKL mechanical keyboard with Cherry MX Brown switches, RGB backlight, and a durable aluminium frame. Tactile and satisfying to type on."),

    Item(name="USB-C Hub",           price=1299,  barcode="100000000003", stock=20,
         description="7-in-1 USB-C hub with 4K HDMI, 100W PD charging, 2x USB-A 3.0, SD card reader, and microSD slot. Compatible with all USB-C laptops."),

    Item(name="Webcam 1080p",        price=3199,  barcode="100000000004", stock=12,
         description="Full HD 1080p webcam with built-in stereo microphone, auto light correction, and plug-and-play USB. Great for video calls and streaming."),

    Item(name="Portable Charger",    price=1899,  barcode="100000000005", stock=25,
         description="20,000mAh power bank with 65W fast charging, dual USB-A + USB-C output, and an LED power indicator. Charges laptops, phones, and tablets."),

    # Accessories
    Item(name="Laptop Stand",        price=999,   barcode="100000000006", stock=30,
         description="Adjustable aluminium laptop stand with six height settings, foldable design, and non-slip pads. Reduces neck strain during long work sessions."),

    Item(name="Mouse Pad XL",        price=599,   barcode="100000000007", stock=40,
         description="Extended gaming mouse pad (90x40cm) with a smooth micro-woven surface, anti-slip rubber base, and stitched edges that resist fraying."),

    Item(name="Cable Organiser",     price=349,   barcode="100000000008", stock=50,
         description="Set of 10 reusable silicone cable ties and a cable management box for keeping your desk tidy. Works with all cable thicknesses."),

    Item(name="Monitor Light Bar",   price=2199,  barcode="100000000009", stock=10,
         description="USB-powered LED monitor light bar with touch controls, adjustable colour temperature (2700K–6500K), and zero screen glare design."),

    Item(name="Ergonomic Mouse",     price=2599,  barcode="100000000010", stock=18,
         description="Vertical ergonomic mouse that keeps your wrist in a natural handshake position. 6 programmable buttons, 1600 DPI, wireless 2.4GHz receiver."),

    # Gaming
    Item(name="Controller Stand",    price=699,   barcode="100000000011", stock=22,
         description="Dual controller charging stand compatible with PS5 and Xbox controllers. LED indicator, 4hr full charge, and a compact footprint for your desk."),

    Item(name="Gaming Headset",      price=3799,  barcode="100000000012", stock=9,
         description="Surround sound gaming headset with 50mm drivers, retractable noise-cancelling mic, memory foam ear cups, and compatibility with PC, PS, and Xbox."),

    # Stationery / Desk
    Item(name="Desk Lamp LED",       price=1499,  barcode="100000000013", stock=14,
         description="Architect-style LED desk lamp with 5 brightness levels, 3 colour modes, USB charging port on the base, and a sturdy clamp mount."),

    Item(name="Notebook A5",         price=299,   barcode="100000000014", stock=60,
         description="A5 hardcover dotted notebook with 200 pages of 100gsm ivory paper. Lay-flat binding, ribbon bookmark, and an elastic closure band."),

    Item(name="Pen Set 12pc",        price=449,   barcode="100000000015", stock=35,
         description="Set of 12 gel pens in assorted colours with 0.5mm tips. Smooth ink flow, quick-dry formula, and comfortable rubber grip for long writing sessions."),
]

with app.app_context():
    added = 0
    skipped = 0
    for item in items:
        exists = Item.query.filter_by(name=item.name).first()
        if not exists:
            db.session.add(item)
            added += 1
        else:
            skipped += 1

    db.session.commit()
    print(f"✅ Done — {added} items added, {skipped} already existed.")