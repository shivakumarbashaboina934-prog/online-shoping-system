# Online Shopping System

A beginner-friendly full-stack online shopping website built with:

- Python Flask
- SQLite
- HTML
- CSS
- JavaScript

## Features

- Home page with products
- Product details
- User registration
- User login/logout
- Password hashing
- Add products to cart
- Update/remove cart items
- Checkout
- Order history
- SQLite database
- Responsive UI

## How to Run on Windows

Open PowerShell inside this project folder.

### 1. Create a virtual environment

```powershell
python -m venv venv
```

### 2. Activate it

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 3. Install packages

```powershell
python -m pip install -r requirements.txt
```

### 4. Start the application

```powershell
python app.py
```

### 5. Open in browser

http://127.0.0.1:5000

The `shop.db` database is created automatically on first run.

## Project Structure

```text
online_shopping_system/
│
├── app.py
├── requirements.txt
├── README.md
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
└── templates/
    ├── base.html
    ├── index.html
    ├── product.html
    ├── login.html
    ├── register.html
    ├── cart.html
    ├── checkout.html
    ├── success.html
    └── orders.html
```

## Important

This is a learning/demo project. For production use, add CSRF protection, secure environment-based secrets, payment-gateway integration, inventory management, admin authentication, input validation, and HTTPS.
