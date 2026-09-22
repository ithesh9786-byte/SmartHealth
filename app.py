import os

from flask import send_from_directory

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask import send_from_directory

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory

from werkzeug.security import generate_password_hash, check_password_hash

from werkzeug.security import check_password_hash, generate_password_hash

from werkzeug.security import check_password_hash, generate_password_hash

import mysql.connector

from google.oauth2 import id_token
from google.auth.transport import requests


app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "smarthealth-secret-key"
)

# =========================================================
# ALLOWED GOOGLE TEST USERS
# =========================================================

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


# =========================================================
# GOOGLE CLIENT ID
# =========================================================

CLIENT_ID = (
    "219197177710-dj8llnafm25i5bmfnf01blt8bgbjfts"
    ".apps.googleusercontent.com"
)


# =========================================================
# MYSQL CONNECTION
# =========================================================

def get_db():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "mysql-c625123-ithesh9786-147c.l.aivencloud.com"),
        port=int(os.environ.get("MYSQL_PORT", 27358)),
        user=os.environ.get("MYSQL_USER", "avnadmin"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE", "defaultdb")
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    try:

        db = get_db()
        db.close()

        return render_template("index.html")

    except Exception as e:

        return f"MySQL Error: {e}"
    
    

@app.route("/")
def index():
    return redirect(url_for("login"))

# =========================================================
# NORMAL LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            # Get user only by email
            query = """
                SELECT * FROM users
                WHERE email = %s
            """

            cursor.execute(query, (email,))

            user = cursor.fetchone()

            if not user:
                return "Email not registered."

            # Check hashed password
            if not check_password_hash(user["password"], password):
                return "Wrong password."

            # Save login session
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            session["name"] = user["name"]

            return redirect(url_for("dashboard"))

        except Exception as e:
            return f"Login Error: {e}"

        finally:
            cursor.close()
            db.close()

    return render_template("login.html")

# =========================================================
# GOOGLE LOGIN
# =========================================================

@app.route("/google-login", methods=["POST"])
def google_login():

    try:

        credential = request.form["credential"]

        user_info = id_token.verify_oauth2_token(
            credential,
            requests.Request(),
            CLIENT_ID
        )

        email = user_info["email"]

        # Check allowed Google users
        if email.lower() not in {
            user.lower()
            for user in ALLOWED_USERS
        }:

            return "Access denied. This Google account is not registered."

        name = user_info.get("name", "")

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        # Create Google user if not already registered
        if not user:

            cursor.execute(
                """
                INSERT INTO users
                (name, email, password)
                VALUES (%s, %s, %s)
                """,
                (
                    name,
                    email,
                    "GOOGLE_LOGIN"
                )
            )

            db.commit()

        # Get user again
        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        # Save session
        session["user_id"] = user.get("id")
        session["email"] = email
        session["name"] = name

        cursor.close()
        db.close()

        return redirect(url_for("dashboard"))

    except Exception as e:

        return f"Google Login Error: {e}"


# =========================================================
# REGISTER
# =========================================================

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
                """
                INSERT INTO users
                (name, email, password)
                VALUES (%s, %s, %s)
                """,
                (
                    name,
                    email,
                    password
                )
            )

            db.commit()

            return (
                "Registration successful! "
                "<a href='/login'>Login</a>"
            )

        except mysql.connector.Error as e:

            return f"Registration Error: {e}"

        finally:

            cursor.close()
            db.close()

    return render_template("register.html")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")

@app.route("/profile")
def profile():

    if "email" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, name, email
            FROM users
            WHERE email = %s
            """,
            (session["email"],)
        )

        user = cursor.fetchone()

        if not user:
            return "User not found."

        return render_template("profile.html", user=user)

    finally:
        cursor.close()
        db.close()

# =========================================================
# SERVICES
# =========================================================

@app.route("/services")
def services():

    return render_template("services.html")


# =========================================================
# BOOKINGS
# =========================================================

@app.route("/bookings")
def bookings():

    if "email" not in session:

        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:

        user_id = session.get("user_id")

        cursor.execute(
            """
            SELECT *
            FROM bookings
            WHERE user_id=%s
            ORDER BY id DESC
            """,
            (user_id,)
        )

        bookings = cursor.fetchall()

        return render_template(
            "bookings.html",
            bookings=bookings
        )

    except mysql.connector.Error as e:

        return f"Booking Error: {e}"

    finally:

        cursor.close()
        db.close()


@app.route("/book", methods=["GET", "POST"])
def book():

    if "email" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        event_name = request.form["event_name"]
        event_date = request.form["event_date"]
        event_time = request.form["event_time"]
        location = request.form["location"]

        user_id = session.get("user_id")

        db = get_db()
        cursor = db.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO bookings
                (
                    user_id,
                    event_name,
                    event_date,
                    event_time,
                    location
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    event_name,
                    event_date,
                    event_time,
                    location
                )
            )

            db.commit()

            return (
                "Booking successful! "
                "<a href='/bookings'>View My Bookings</a>"
            )

        except mysql.connector.Error as e:

            return f"Booking Error: {e}"

        finally:

            cursor.close()
            db.close()

    return render_template("book.html")


# =========================================================
# BMI CALCULATOR
# =========================================================


@app.route("/bmi", methods=["GET", "POST"])
def bmi():

    bmi_value = None
    category = None

    if request.method == "POST":

        height = float(request.form["height"])
        weight = float(request.form["weight"])

        height_m = height / 100

        bmi_value = weight / (height_m * height_m)
        bmi_value = round(bmi_value, 2)

        if bmi_value < 18.5:
            category = "Underweight"
        elif bmi_value < 25:
            category = "Normal weight"
        elif bmi_value < 30:
            category = "Overweight"
        else:
            category = "Obesity"

    return render_template(
        "bmi.html",
        bmi=bmi_value,
        category=category
    )

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


def bmi():
    bmi_value = None
    category = None

    if request.method == "POST":
        height = float(request.form["height"])
        weight = float(request.form["weight"])

        height_m = height / 100
        bmi_value = weight / (height_m * height_m)

        if bmi_value < 18.5:
            category = "Underweight"
        elif bmi_value < 25:
            category = "Normal weight"
        elif bmi_value < 30:
            category = "Overweight"
        else:
            category = "Obesity"

    return render_template(
        "bmi.html",
        bmi=bmi_value,
        category=category
    )

# =========================================================
# FAVICON
# =========================================================

@app.route("/favicon.ico")
def favicon():
    return send_from_directory("static", "icon-192.png")

# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    print("")
    print("========================================")
    print("        SmartHealth Application")
    print("========================================")
    print("")
    print(f"Open: http://127.0.0.1:{port}/login")
    print("")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )
