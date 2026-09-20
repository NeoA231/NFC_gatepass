import datetime
from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from db.database import close_db, get_db, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = "qwertyBOARD"

app.teardown_appcontext(close_db)

@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("Initialised the SQLite database.")

# 1. Student Registration
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    required = ["student_number", "full_name", "password", "phone", "residence_address"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    hashed_pw = generate_password_hash(data["password"])
    db = get_db()

    try:
        cursor = db.execute(
            """
            INSERT INTO students (student_number, full_name, password_hash, phone, residence_address)
            VALUES (?, ?, ?, ?, ?)
            """,
            (data["student_number"], data["full_name"], hashed_pw, data["phone"], data["residence_address"])
        )
        db.commit()
    except db.IntegrityError:
        return jsonify({"error": "Student number already registered"}), 400

    return jsonify({"message": "Student registered successfully", "student_id": cursor.lastrowid}), 201

# 2. Tag Provisioning
@app.route("/api/tags/provision", methods=["POST"])
def provision_tag():
    data = request.get_json() or {}
    tag_uid = data.get("tag_uid")
    if not tag_uid:
        return jsonify({"error": "tag_uid required"}), 400

    db = get_db()
    try:
        # Fixed typo 'INSERT' and added trailing comma for a valid single-item tuple
        db.execute("INSERT INTO gatepasses (tag_uid) VALUES (?)", (tag_uid,))
        db.commit()
    except db.IntegrityError:
        return jsonify({"error": "Tag already provisioned"}), 409

    return jsonify({"message": "Tag provisioned with null data", "tag_uid": tag_uid}), 201

# 3. Laptop Registration / Tag Claim
@app.route("/api/gatepass/claim", methods=["POST"])
def claim_tag():
    data = request.get_json() or {}
    required = ["tag_uid", "student_id", "laptop_model", "serial_number"]

    if not all(field in data for field in required):
        return jsonify({"error": "Missing hardware registration fields"}), 400

    db = get_db()
    tag = db.execute("SELECT * FROM gatepasses WHERE tag_uid = ?", (data["tag_uid"],)).fetchone()

    if not tag:
        return jsonify({"error": "Invalid or unprovisioned NFC tag"}), 404
    if tag["student_id"] is not None:
        return jsonify({"error": "Tag has already been claimed"}), 409

    try:
        # Added serial_number and WHERE tag_uid clause to target only this specific tag
        db.execute(
            """
            UPDATE gatepasses
            SET student_id = ?, laptop_model = ?, serial_number = ?, registered_at = ?
            WHERE tag_uid = ?
            """,
            (
                data["student_id"],
                data["laptop_model"],
                data["serial_number"],
                datetime.datetime.now(datetime.timezone.utc),
                data["tag_uid"]
            )
        )
        db.commit()
    except db.IntegrityError:
        return jsonify({"error": "Laptop serial number already exists in system"}), 409

    return jsonify({"message": "Gatepass successfully linked"}), 200

@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        data = request.form
        required = ["student_number", "full_name", "password", "residence_address", 'phone']
        if not all(field in data and data[field].strip() for field in required):
            return render_template("register.html", error="All Fields are required.")

        hashed_pw = generate_password_hash(data["password"])
        db = get_db()

        try:
            db.execute(
                """
                INSERT INTO students (student_number, full_name, password_hash, phone, residence_address)
                VALUES (?, ?, ?, ?, ?)
                """,
                (data["student_number"].strip(), data["full_name"].strip(), hashed_pw, data["phone"].strip(), data["residence_address"].strip())
            )
            db.commit()
            return render_template("register.html",success="Student profile registered successfully! You can now Login.")

        except db.IntegrityError:
            return render_template("register.html", error="The student number is already registered.")

    return render_template("register.html")

@app.route("/admin/students", methods=["GET"])
def admin_students_page():
    db = get_db()
    records = db.execute(
        """
        SELECT 
            s.id AS student_id,
            s.student_number,
            s.full_name,
            s.phone,
            s.residence_address,
            s.created_at,
            g.tag_uid,
            g.laptop_model,
            g.serial_number,
            g.is_active
        FROM students s
        LEFT JOIN gatepasses g ON s.id = g.student_id
        ORDER BY s.created_at DESC
        """
    ).fetchall()

    return render_template("admin_students.html", records=records)

# Student login page and handler
@app.route("/login", methods=["GET","POST"])
def login_page():
    if "student_id" in session:
        return redirect(url_for("dashboard_page"))

    if request.method == "POST":
        student_number = request.form.get("student_number", "").strip()
        password = request.form.get("password", "").strip()

        if not student_number or not password:
            return render_template("login.html", error="please provide both your student number and password")

        db = get_db()
        student = db.execute(
            "SELECT * FROM students WHERE student_number = ?",
            (student_number,)
        ).fetchone()

        if not student or not check_password_hash(student["password_hash"], password):
            return render_template("login.html", error="invalid student number or password")

        session.clear()
        session["student_id"] = student["id"]
        session["student_number"] = student["student_number"]
        session["full_name"] = student["full_name"]

        return redirect(url_for("dashboard_page"))
    return render_template("login.html")


# Student Protected Dashboard
@app.route("/dashboard", methods=["GET"])
def dashboard_page():
    if "student_id" not in session:
        return redirect(url_for("login_page"))

    db = get_db()
    # Fetch student profile details
    student = db.execute(
        "SELECT * FROM students WHERE id = ?", (session["student_id"],)
    ).fetchone()

    # Fetch any gatepasses linked to this student
    gatepass = db.execute(
        "SELECT * FROM gatepasses WHERE student_id = ?", (session["student_id"],)
    ).fetchone()

    return render_template("dashboard.html", student=student, gatepass=gatepass)


# Student Logout Handler
@app.route("/logout", methods=["POST"])
def logout_page():
    session.clear()
    return redirect(url_for("login_page"))