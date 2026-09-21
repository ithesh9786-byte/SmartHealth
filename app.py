from flask import Flask, render_template, request, redirect, session
import os
import mysql.connector

from werkzeug.security import generate_password_hash, check_password_hash

from google.oauth2 import id_token
from google.auth.transport import requests


app = Flask(__name__)

# Session secret
app.secret_key = os.environ.get("SECRET_KEY", "smarthealth-secret-key")


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

CLIENT_ID = "219197177710-dj8llnafm25i5bmfnf01blt8bgbjfts.apps.googleusercontent.com"


# =========================================================
# MYSQL CONNECTION
# =========================================================

def get_db():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST"),
        port=int(os.environ.get("MYSQL_PORT", 3306)),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE")
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


# =========================================================
# NORMAL LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:

            cursor.execute(
                "SELECT * FROM users WHERE email=%s",
                (email,)
            )

            user = cursor.fetchone()

            if user and check_password_hash(
                user["password"],
                password
            ):

                session["user_id"] = user.get("id")
                session["email"] = user["email"]
                session["name"] = user.get("name", "")

                return redirect("/")

            return "Invalid email or password."

        except Exception as e:

            return f"Login Error: {e}"

        finally:

            cursor.close()
            db.close()

    return render_template("login.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Hash password
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


# =========================================================
# GOOGLE LOGIN
# =========================================================

@app.route("/google-login", methods=["POST"])
def google_login():

    try:

        # Get Google credential
        credential = request.form["credential"]

        # Verify Google token
        user_info = id_token.verify_oauth2_token(
            credential,
            requests.Request(),
            CLIENT_ID
        )

        # Get Google email
        email = user_info["email"]

        # =================================================
        # CHECK ALLOWED GOOGLE USERS
        # =================================================

        if email.lower() not in {
            user.lower() for user in ALLOWED_USERS
        }:

            return "Access denied. This Google account is not registered."


        # Get Google name
        name = user_info.get("name", "")


        # =================================================
        # CONNECT MYSQL
        # =================================================

        db = get_db()
        cursor = db.cursor(dictionary=True)


        # Check whether user already exists
        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()


        # =================================================
        # CREATE USER IF NOT EXISTS
        # =================================================

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


        # =================================================
        # SAVE LOGIN SESSION
        # =================================================

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        session["user_id"] = user.get("id")
        session["email"] = email
        session["name"] = name


        cursor.close()
        db.close()


        return redirect("/dashboard")


    except Exception as e:

        return f"Google Login Error: {e}"
@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        return redirect("/login")

    return "SmartHealth Dashboard - Login Successful!"

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
