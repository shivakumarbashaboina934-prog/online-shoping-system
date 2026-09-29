from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DB = "shop.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        image TEXT
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total REAL NOT NULL,
        status TEXT DEFAULT 'Placed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    );
    """)

    count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if count == 0:
        products = [
            ("Wireless Headphones", "Comfortable Bluetooth headphones with clear sound.", 1499, "🎧"),
            ("Smart Watch", "Fitness tracking, notifications and stylish design.", 2499, "⌚"),
            ("Running Shoes", "Lightweight sports shoes for everyday running.", 1999, "👟"),
            ("Laptop Backpack", "Water-resistant backpack with laptop compartment.", 999, "🎒"),
            ("Smartphone", "Fast processor, great camera and long battery life.", 14999, "📱"),
            ("Cotton T-Shirt", "Soft premium cotton T-shirt for daily wear.", 599, "👕"),
            ("Bluetooth Speaker", "Portable speaker with powerful sound.", 1299, "🔊"),
            ("Sunglasses", "Classic UV-protection sunglasses.", 799, "🕶️")
        ]
        conn.executemany(
            "INSERT INTO products (name, description, price, image) VALUES (?, ?, ?, ?)",
            products
        )
    conn.commit()
    conn.close()

@app.context_processor
def inject_cart_count():
    cart = session.get("cart", {})
    return {"cart_count": sum(cart.values())}

@app.route("/")
def home():
    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", products=products)

@app.route("/product/<int:product_id>")
def product(product_id):
    conn = get_db()
    item = conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
    conn.close()
    if not item:
        flash("Product not found.", "error")
        return redirect(url_for("home"))
    return render_template("product.html", product=item)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (name,email,password) VALUES (?,?,?)",
                (name, email, generate_password_hash(password))
            )
            conn.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered.", "error")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash("Login successful.", "success")
            return redirect(url_for("home"))

        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_name", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

@app.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    conn = get_db()
    item = conn.execute("SELECT id FROM products WHERE id=?", (product_id,)).fetchone()
    conn.close()

    if not item:
        flash("Product not found.", "error")
        return redirect(url_for("home"))

    cart = session.get("cart", {})
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart
    flash("Product added to cart.", "success")
    return redirect(request.referrer or url_for("home"))

@app.route("/cart")
def cart():
    cart_data = session.get("cart", {})
    items = []
    total = 0

    conn = get_db()
    for product_id, quantity in cart_data.items():
        item = conn.execute(
            "SELECT * FROM products WHERE id=?", (int(product_id),)
        ).fetchone()
        if item:
            subtotal = item["price"] * quantity
            total += subtotal
            items.append({"product": item, "quantity": quantity, "subtotal": subtotal})
    conn.close()

    return render_template("cart.html", items=items, total=total)

@app.route("/update-cart/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    quantity = int(request.form.get("quantity", 1))
    cart = session.get("cart", {})
    key = str(product_id)

    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity

    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/remove-from-cart/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "user_id" not in session:
        flash("Please login before checkout.", "error")
        return redirect(url_for("login"))

    cart_data = session.get("cart", {})
    if not cart_data:
        flash("Your cart is empty.", "error")
        return redirect(url_for("cart"))

    conn = get_db()
    items = []
    total = 0
    for product_id, quantity in cart_data.items():
        item = conn.execute(
            "SELECT * FROM products WHERE id=?", (int(product_id),)
        ).fetchone()
        if item:
            subtotal = item["price"] * quantity
            total += subtotal
            items.append((item, quantity, subtotal))

    if request.method == "POST":
        order = conn.execute(
            "INSERT INTO orders (user_id,total) VALUES (?,?)",
            (session["user_id"], total)
        )
        order_id = order.lastrowid

        for item, quantity, subtotal in items:
            conn.execute(
                "INSERT INTO order_items (order_id,product_id,quantity,price) VALUES (?,?,?,?)",
                (order_id, item["id"], quantity, item["price"])
            )
        conn.commit()
        conn.close()

        session["cart"] = {}
        return render_template("success.html", order_id=order_id, total=total)

    conn.close()
    return render_template("checkout.html", items=items, total=total)

@app.route("/orders")
def orders():
    if "user_id" not in session:
        flash("Please login to view your orders.", "error")
        return redirect(url_for("login"))

    conn = get_db()
    orders = conn.execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC",
        (session["user_id"],)
    ).fetchall()
    conn.close()
    return render_template("orders.html", orders=orders)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
