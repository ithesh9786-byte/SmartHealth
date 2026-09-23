import os

from flask import send_from_directory

from workout_data import WORKOUT_DATA

from werkzeug.utils import secure_filename

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

# ==============================
# PROFILE IMAGE UPLOAD
# ==============================

UPLOAD_FOLDER = os.path.join("static", "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

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
    "219197177710-dj8llnafm25i5bmfnf01blt8bgbjftsf.apps.googleusercontent.com"
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

    return render_template(
    "login.html",
    google_client_id="219197177710-dj8llnafm25i5bmfnf01blt8bgbjftsf.apps.googleusercontent.com"
)

# =========================================================
# GOOGLE LOGIN
# =========================================================

@app.route("/google-login", methods=["POST"])
def google_login():

    db = None
    cursor = None

    try:

        # Get Google credential
        credential = request.form.get("credential")

        if not credential:
            return "Google login failed: credential not received."

        # Verify Google ID token
        user_info = id_token.verify_oauth2_token(
            credential,
            requests.Request(),
            CLIENT_ID
        )

        # Check email
        email = user_info.get("email", "").lower().strip()
        name = user_info.get("name", "Google User")

        if not email:
            return "Google login failed: email not received."

        # Check email verification
        if not user_info.get("email_verified", False):
            return "Google email is not verified."

        # Allowed users
        allowed_users = {
            user.lower()
            for user in ALLOWED_USERS
        }

        if email not in allowed_users:
            return (
                "Access denied. This Google account "
                "is not registered for SmartHealth."
            )

        # Database
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Check user
        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        # Create user if not exists
        if not user:

            random_password = generate_password_hash(
                os.urandom(32).hex()
            )

            cursor.execute(
                """
                INSERT INTO users
                (name, email, password)
                VALUES (%s, %s, %s)
                """,
                (
                    name,
                    email,
                    random_password
                )
            )

            db.commit()

            # Get newly created user
            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            user = cursor.fetchone()

        # Save session
        session["user_id"] = user["id"]
        session["email"] = user["email"]
        session["name"] = user["name"]

        return redirect(url_for("dashboard"))

    except Exception as e:

        return f"Google Login Error: {e}"

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()

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

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "email" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:

        # ==================================
        # UPDATE PROFILE
        # ==================================

        if request.method == "POST":

            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone = request.form.get("phone", "").strip()

            date_of_birth = (
                request.form.get("date_of_birth")
                or None
            )

            gender = (
                request.form.get("gender")
                or None
            )

            location = request.form.get(
                "location",
                ""
            ).strip()


            # Required fields

            if not name or not email:

                flash(
                    "Name and email are required."
                )

                return redirect(
                    url_for("profile")
                )


            # ==================================
            # GET OLD PROFILE IMAGE
            # ==================================

            cursor.execute(
                """
                SELECT profile_image
                FROM users
                WHERE id = %s
                """,
                (session["user_id"],)
            )

            old_user = cursor.fetchone()

            profile_image = (
                old_user["profile_image"]
                if old_user
                else None
            )


            # ==================================
            # PROFILE PHOTO
            # ==================================

            photo = request.files.get(
                "profile_image"
            )

            if photo and photo.filename:

                filename = secure_filename(
                    photo.filename
                )

                if "." not in filename:

                    flash(
                        "Invalid image file."
                    )

                    return redirect(
                        url_for("profile")
                    )


                extension = (
                    filename
                    .rsplit(".", 1)[1]
                    .lower()
                )


                if extension not in ALLOWED_EXTENSIONS:

                    flash(
                        "Only image files are allowed."
                    )

                    return redirect(
                        url_for("profile")
                    )


                new_filename = (
                    f"user_{session['user_id']}."
                    f"{extension}"
                )


                photo.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        new_filename
                    )
                )


                profile_image = (
                    f"uploads/{new_filename}"
                )


            # ==================================
            # UPDATE MYSQL
            # ==================================

            cursor.execute(
                """
                UPDATE users
                SET
                    name = %s,
                    email = %s,
                    phone = %s,
                    date_of_birth = %s,
                    gender = %s,
                    location = %s,
                    profile_image = %s
                WHERE id = %s
                """,
                (
                    name,
                    email,
                    phone,
                    date_of_birth,
                    gender,
                    location,
                    profile_image,
                    session["user_id"]
                )
            )

            db.commit()


            # ==================================
            # UPDATE SESSION
            # ==================================

            session["name"] = name
            session["email"] = email


            flash(
                "Profile updated successfully!"
            )

            return redirect(
                url_for("profile")
            )


        # ==================================
        # LOAD PROFILE
        # ==================================

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                phone,
                date_of_birth,
                gender,
                location,
                profile_image
            FROM users
            WHERE id = %s
            """,
            (session["user_id"],)
        )

        user = cursor.fetchone()


        if not user:

            return "User not found.", 404


        initials = get_initials(
            user["name"]
        )


        return render_template(
            "profile.html",
            user=user,
            initials=initials
        )


    except mysql.connector.IntegrityError:

        db.rollback()

        flash(
            "This email is already used."
        )

        return redirect(
            url_for("profile")
        )


    except Exception as e:

        db.rollback()

        return f"Profile Error: {e}"


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
# DIET MANAGEMENT
# =========================================================

@app.route("/diet", methods=["GET", "POST"])
def diet():

    if "email" not in session:
        return redirect(url_for("login"))

    diet_plan = None

    if request.method == "POST":

        age = int(request.form["age"])
        gender = request.form["gender"]
        height = float(request.form["height"])
        weight = float(request.form["weight"])
        goal = request.form["goal"]
        activity = request.form["activity"]

        # BMI
        height_m = height / 100
        bmi = weight / (height_m * height_m)

        # Basic calorie calculation
        if gender == "Male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        # Activity multiplier
        if activity == "Low":
            calories = bmr * 1.2
        elif activity == "Moderate":
            calories = bmr * 1.55
        else:
            calories = bmr * 1.725

        # Goal adjustment
        if goal == "Weight Gain":
            calories += 300
            protein = int(weight * 1.6)

            breakfast = "Oats + Milk + Banana + Eggs"
            morning_snack = "Nuts + Fruit"
            lunch = "Rice + Chicken/Paneer + Vegetables"
            evening_snack = "Banana Shake + Peanut Butter"
            dinner = "Chapati/Rice + Eggs + Vegetables"

        elif goal == "Weight Loss":
            calories -= 300
            protein = int(weight * 1.6)

            breakfast = "Oats + Eggs + Fruit"
            morning_snack = "Fruit + Nuts"
            lunch = "Rice + Vegetables + Chicken/Paneer"
            evening_snack = "Green Tea + Fruit"
            dinner = "Chapati + Vegetables + Protein"

        else:
            calories = calories
            protein = int(weight * 1.2)

            breakfast = "Oats + Milk + Eggs"
            morning_snack = "Fruit + Nuts"
            lunch = "Rice + Vegetables + Protein"
            evening_snack = "Fruit + Yogurt"
            dinner = "Chapati + Vegetables + Eggs"

        calories = int(calories)

        # Save to MySQL
        db = get_db()
        cursor = db.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO diet_plans
                (
                    user_id,
                    goal,
                    calories,
                    protein,
                    breakfast,
                    morning_snack,
                    lunch,
                    evening_snack,
                    dinner
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    session["user_id"],
                    goal,
                    calories,
                    protein,
                    breakfast,
                    morning_snack,
                    lunch,
                    evening_snack,
                    dinner
                )
            )

            db.commit()

            diet_plan = {
                "bmi": round(bmi, 2),
                "goal": goal,
                "calories": calories,
                "protein": protein,
                "breakfast": breakfast,
                "morning_snack": morning_snack,
                "lunch": lunch,
                "evening_snack": evening_snack,
                "dinner": dinner
            }

        except mysql.connector.Error as e:

            return f"Diet Error: {e}"

        finally:

            cursor.close()
            db.close()

    return render_template(
        "diet.html",
        diet_plan=diet_plan
    )

@app.route("/workout-schedule")
def workout_schedule():
    return render_template("workout_schedule.html")


@app.route("/workout/<category>")
def workout_days(category):
    return render_template(
        "workout_days.html",
        category=category
    )

@app.route("/workout/<category>/<int:day>")
def workout_day(category, day):
    workout = WORKOUT_DATA.get(category, {}).get(day)

    if not workout:
        return "Workout plan not found", 404

    return render_template(
        "workout_day.html",
        category=category,
        day=day,
        workout=workout
    )
    
# =========================================================
# MY DIET PLAN
# =========================================================

@app.route("/my-diet")
def my_diet():

    if "email" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT *
            FROM diet_plans
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (session["user_id"],)
        )

        diet_plan = cursor.fetchone()

        return render_template(
            "my_diet.html",
            diet_plan=diet_plan
        )

    except mysql.connector.Error as e:

        return f"My Diet Error: {e}"

    finally:

        cursor.close()
        db.close()

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
