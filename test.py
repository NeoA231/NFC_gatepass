from flask import Flask, render_template, request, redirect, url_for, session


# ============================================================
# FLASK CONFIGURATION
# ============================================================

app = Flask(
    __name__,
    template_folder="frontend",
    static_folder="frontend",
    static_url_path="/static"
)

app.secret_key = "nfc-gatepass-development-key"


# ============================================================
# TEMPORARY TEST DATA
# ============================================================

students = [
    {
        "student_number": "VUT2024001",
        "full_name": "Test Student",
        "phone": "071 234 5678",
        "residence_address": "VUT Student Residence"
    },
    {
        "student_number": "VUT2024002",
        "full_name": "Another Student",
        "phone": "072 345 6789",
        "residence_address": "Private Residence"
    }
]


gatepasses = {
    "VUT2024001": {
        "tag_uid": "04A1B2C3D4E5",
        "laptop_model": "Dell Latitude 5420",
        "serial_number": "DL5420-TEST-001"
    }
}


# ============================================================
# STATIC FILE ROUTES
# ============================================================
#
# Our static files are located inside:
#
# frontend/css/
# frontend/js/
#
# Therefore:
#
# /static/css/style.css
# /static/js/login.js
# /static/js/dashboard.js
# /static/js/admin.js
#
# will be served from the frontend folder.
# ============================================================


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():
    return redirect(url_for("login"))


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        student_number = request.form.get("student_number")
        password = request.form.get("password")

        # Temporary login system.
        # Password is currently not checked because we are
        # testing the frontend before connecting the database.

        student = next(
            (
                student
                for student in students
                if student["student_number"] == student_number
            ),
            None
        )

        if student:

            session["student_number"] = student["student_number"]
            session["role"] = "student"

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid student number or password."
        )

    return render_template("login.html")


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        student_number = request.form.get("student_number")
        full_name = request.form.get("full_name")
        phone = request.form.get("phone")
        residence_address = request.form.get("residence_address")
        password = request.form.get("password")

        new_student = {
            "student_number": student_number,
            "full_name": full_name,
            "phone": phone,
            "residence_address": residence_address
        }

        students.append(new_student)

        session["student_number"] = student_number
        session["role"] = "student"

        return redirect(url_for("dashboard"))

    return render_template("register.html")


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    student_number = session.get("student_number")

    if not student_number:
        return redirect(url_for("login"))

    student = next(
        (
            student
            for student in students
            if student["student_number"] == student_number
        ),
        None
    )

    if not student:
        session.clear()
        return redirect(url_for("login"))

    gatepass = gatepasses.get(student_number)

    return render_template(
        "dashboard.html",
        student=student,
        gatepass=gatepass
    )


# ============================================================
# CLAIM / REGISTER LAPTOP
# ============================================================

@app.route("/claim", methods=["GET", "POST"])
def claim():
    student_number = session.get("student_number")

    if not student_number:
        return redirect(url_for("login"))

    if request.method == "POST":
        tag_uid = request.form.get("tag_uid")
        laptop_model = request.form.get("laptop_model")
        serial_number = request.form.get("serial_number")

        gatepasses[student_number] = {
            "tag_uid": tag_uid,
            "laptop_model": laptop_model,
            "serial_number": serial_number
        }

        return redirect(url_for("dashboard"))

    return render_template("claim.html")


# ============================================================
# ADMIN
# ============================================================

@app.route("/admin")
def admin():

    # Temporary admin access for frontend testing.
    session["role"] = "admin"

    return redirect(url_for("admin_students"))


# ============================================================
# ADMIN STUDENT REGISTRY
# ============================================================

@app.route("/admin/students")
def admin_students():

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    records = []

    for student in students:

        gatepass = gatepasses.get(
            student["student_number"]
        )

        record = {
            "student_number": student["student_number"],
            "full_name": student["full_name"],
            "phone": student["phone"],
            "residence_address": student["residence_address"],

            "tag_uid": (
                gatepass["tag_uid"]
                if gatepass
                else None
            ),

            "laptop_model": (
                gatepass["laptop_model"]
                if gatepass
                else None
            ),

            "serial_number": (
                gatepass["serial_number"]
                if gatepass
                else None
            )
        }

        records.append(record)

    return render_template(
        "admin_students.html",
        records=records
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return redirect(url_for("login"))


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
