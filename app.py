import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST"),
        port=int(os.environ.get("MYSQL_PORT", 3306)),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE")
    )
@app.route("/")
def home():

    try:
        db = get_db()
        db.close()
        return render_template("index.html")
    except Exception as e:
        return f"MySQL Error: {e}"
@app.route("/google-login", methods=["POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user:
            return redirect(url_for("dashboard"))

        return "Invalid email or password"

    return render_template("login.html")
def google_login():
    try:
        credential = request.form["credential"]

        CLIENT_ID = "219197177710-dj8llnafm25i5bmfnf01blt8bgbjfts.apps.googleusercontent.com"

        user_info = id_token.verify_oauth2_token(
            credential,
            requests.Request(),
            CLIENT_ID
        )

        email = user_info["email"]

# Allowed Google test users
ALLOWED_USERS = {
    "ithesh9786@gmail.com",
    "s16678524@gmail.com",
    "premkumarpaveen@gmail.com",
    "amarnath8610526257@gmail.com",
    "gnithishkumar2006@gmail.com",
    "harinisrignanavel@gmail.com",
    "srirammm1333@gmail.com",
    "mageshmagim012@gmail.com",
    "vasanthraj145@gmail.com",
    "rdurga7002@gmail.com",
    "ragavi2470@gmail.com",
    "mugil.murugan0@gmail.com",
    "rajarivazhan2007@gmail.com",
    "elanthamizhanj07@gmail.com",
    "ap9384410@gmail.com",
    "naveenanatarajan123@gmail.com",
    "kuganjvk@gmail.com",
    "abipriya2926@gmail.com",
    "premav3004@gmail.com",
    "munnisha.8610@gmail.com",
    "nivedhaarumugam77@gmail.com",
    "ndharani007@gmail.com",
    "keerthivasan3534@gmail.com",
    "leoprabhu149@gmail.com",
    "syedkutbudeen0@gmail.com",
    "mmanandh33@gmail.com",
    "sujisujitha7002@gmail.com",
    "amirthasenthilkumar26@gmail.com",
    "raji875438@gmail.com",
    "kalai9791986813@gmail.com",
    "maindupriya@gmail.com",
    "saravanan8903764645@gmail.com",
    "jajagatheesh34@gmail.com",
    "mohanrajmalar55@gmail.com"
}

if email.lower() not in {user.lower() for user in ALLOWED_USERS}:
    return "Access denied. This Google account is not registered."

        name = user_info.get("name", "")

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, "GOOGLE_LOGIN")
            )
            db.commit()

        cursor.close()
        db.close()

        return redirect(url_for("dashboard"))

    except Exception as e:
        return f"Google Login Error: {e}"  
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        password = generate_password_hash(password)

        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password)
            )
            db.commit()
            return "Registration successful! <a href='/login'>Login</a>"

        except mysql.connector.Error as e:
            return f"Registration Error: {e}"

        finally:
            cursor.close()
            db.close()

    return render_template("register.html")
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")
@app.route("/services")
def services():
    return render_template("services.html")
@app.route("/bookings")
def bookings():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM bookings WHERE user_id = %s ORDER BY id DESC",
        (2,)
    )

    bookings = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("bookings.html", bookings=bookings)
@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        event_name = request.form["event_name"]
        event_date = request.form["event_date"]
        event_time = request.form["event_time"]
        location = request.form["location"]

        # Test user ID = 2
        user_id = 2

        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute(
                """INSERT INTO bookings
                   (user_id, event_name, event_date, event_time, location)
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, event_name, event_date, event_time, location)
            )

            db.commit()

            return "Booking successful! <a href='/bookings'>View My Bookings</a>"

        except mysql.connector.Error as e:
            return f"Booking Error: {e}"

        finally:
            cursor.close()
            db.close()

    return render_template("book.html")
@app.route("/logout")
def logout():
    return redirect(url_for("login"))
if __name__ == "__main__":
    app.run(debug=True)
