# 🛒 Flask E-Commerce App

A full-stack e-commerce web app built with Flask — supports user accounts, product browsing, a shopping cart, order checkout, and product reviews.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 Auth | User registration and login |
| 🛍️ Products | Product listing and detail pages |
| 🛒 Cart | Add to cart and checkout flow |
| ⭐ Reviews | Product reviews and ratings |
| 🖼️ Images | Image upload support for products |

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, Flask, SQLAlchemy, Flask-Login |
| **Database** | SQLite |
| **Frontend** | Bootstrap |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/flask-market.git
cd flask-market
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your `.env` file
```env
SECRET_KEY=your_secret_key
```

### 5. Run the app
```bash
python run.py
```
> Then open `http://localhost:5000` in your browser.

---

## 📸 Screenshots

<img width="1914" alt="Home" src="https://github.com/user-attachments/assets/a69ffd60-1def-4a01-a345-0020b1dec861" />

<img width="1127" alt="Products" src="https://github.com/user-attachments/assets/c1f2c96e-0e33-4c73-b6d4-41c1d59180db" />

<img width="1864" alt="Cart" src="https://github.com/user-attachments/assets/cb8a74f5-dbf7-44c7-b07b-2dc58f5c6a66" />

<img width="1874" alt="Checkout" src="https://github.com/user-attachments/assets/692a0ce5-10e4-4a20-8c4f-d7700e43b56a" />

<img width="1726" alt="Orders" src="https://github.com/user-attachments/assets/7a86219a-e173-464d-b219-d51cb83f3969" />

---

## 📌 Notes

> ⚠️ The SQLite database isn't included. You'll need to run migrations or seed it manually before the app works.
