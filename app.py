from flask import Flask, render_template, request, redirect, url_for,jsonify
import sqlite3
import os

app = Flask(__name__)

# @app.route('/')
# def home():
#     return "Hello Railway!"

# # Required for deployment
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)

# ------------------ DATABASE ------------------
def init_db():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ------------------ ROUTES ------------------

# Home → Login first
@app.route("/")
def home():
    return redirect(url_for("login"))

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Login ❌"

    return render_template("login.html")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/add", methods=["POST"])
def add():
    data = request.json

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            category TEXT,
            amount REAL,
            date TEXT
        )
    """)

    cursor.execute(
        "INSERT INTO transactions (type, category, amount, date) VALUES (?, ?, ?, ?)",
        (data["type"], data["category"], data["amount"], data["date"])
    )

    conn.commit()
    conn.close()

    return {"message": "Added"}


@app.route("/data")
def data():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()

    conn.close()
    return jsonify(rows)


@app.route("/insights")
def insights():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT type, amount FROM transactions")
    data = cursor.fetchall()

    conn.close()

    income = sum(x[1] for x in data if x[0] == "Income")
    expense = sum(x[1] for x in data if x[0] == "Expense")

    # ✅ ADD THIS LINE
    balance = income - expense

    message = "✅ Good control"
    if expense > income:
        message = "⚠️ Overspending!"

    return jsonify({
        "income": income,
        "expense": expense,
        "balance": balance,   # ✅ ADD THIS
        "message": message
    })
@app.route("/monthly")
def monthly():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT substr(date, 1, 7) as month, type, SUM(amount)
        FROM transactions
        GROUP BY month, type
        ORDER BY month
    """)

    rows = cursor.fetchall()
    conn.close()

    result = {}

    for month, t_type, amount in rows:
        if month not in result:
            result[month] = {"income": 0, "expense": 0}

        if t_type == "Income":
            result[month]["income"] = amount
        else:
            result[month]["expense"] = amount

    # ✅ calculate balance
    for month in result:
        result[month]["balance"] = result[month]["income"] - result[month]["expense"]

    return jsonify(result)
@app.route("/delete/<int:id>", methods=["DELETE"])
def delete(id):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM transactions WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Deleted successfully"})

# Dashboard
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# import os

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 10000))
#     app.run(host="0.0.0.0", port=port)
# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(debug=True)
