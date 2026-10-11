import datetime
import sqlite3
from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from db.database import close_db, get_db, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = "qwertyBOARD"

app.teardown_appcontext(close_db)

@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("Initialized the SQLite database.")

@app.route("/")
def index():
    if "student_id" in session:
        return redirect(url_for("dashboard_page"))
    return redirect(url_for("login_page"))

# 1. Student Registration
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    required = ["student_number", "full_name", "password", "phone", "residence_address"]
    if not all(field in data and str(data[field]).strip() for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    hashed_pw = generate_password_hash(data["password"])
    db = get_db()

    try:
        cursor = db.execute(
            """
            INSERT INTO students (student_number, full_name, password_hash, phone, residence_address)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(data["student_number"]).strip(),
                str(data["full_name"]).strip(),
                hashed_pw,
                str(data["phone"]).strip(),
                str(data["residence_address"]).strip()
            )
        )
        db.commit()
    except (sqlite3.IntegrityError, db.IntegrityError):
        return jsonify({"error": "Student number already registered"}), 400

    return jsonify({"message": "Student registered successfully", "student_id": cursor.lastrowid}), 201

# 2. Tag Provisioning
@app.route("/api/tags/provision", methods=["POST"])
def provision_tag():
    data = request.get_json(silent=True) or {}
    tag_uid = data.get("tag_uid")
    if not tag_uid or not str(tag_uid).strip():
        return jsonify({"error": "tag_uid required"}), 400

    tag_uid = str(tag_uid).strip()
    db = get_db()
    try:
        db.execute("INSERT INTO gatepasses (tag_uid) VALUES (?)", (tag_uid,))
        db.commit()
    except (sqlite3.IntegrityError, db.IntegrityError):
        return jsonify({"error": "Tag already provisioned"}), 409

    return jsonify({"message": "Tag provisioned with null data", "tag_uid": tag_uid}), 201

# 3. Laptop Registration / Tag Claim
@app.route("/api/gatepass/claim", methods=["POST"])
def claim_tag():
    data = request.get_json(silent=True) or {}
    required = ["tag_uid", "student_id", "laptop_model", "serial_number"]

    if not all(field in data and (data[field] is not None and str(data[field]).strip() != "") for field in required):
        return jsonify({"error": "Missing hardware registration fields"}), 400

    tag_uid = str(data["tag_uid"]).strip()
    student_id = data["student_id"]
    laptop_model = str(data["laptop_model"]).strip()
    serial_number = str(data["serial_number"]).strip()

    db = get_db()
    tag = db.execute("SELECT * FROM gatepasses WHERE tag_uid = ?", (tag_uid,)).fetchone()

    if not tag:
        return jsonify({"error": "Invalid or unprovisioned NFC tag"}), 404
    if tag["student_id"] is not None:
        return jsonify({"error": "Tag has already been claimed"}), 409

    student = db.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    existing_pass = db.execute("SELECT id FROM gatepasses WHERE student_id = ?", (student_id,)).fetchone()
    if existing_pass:
        return jsonify({"error": "Student already has an active gatepass"}), 409

    existing_serial = db.execute("SELECT id FROM gatepasses WHERE serial_number = ?", (serial_number,)).fetchone()
    if existing_serial:
        return jsonify({"error": "Laptop serial number already exists in the system"}), 409

    now_ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    try:
        db.execute(
            """
            UPDATE gatepasses
            SET student_id = ?, laptop_model = ?, serial_number = ?, registered_at = ?
            WHERE tag_uid = ?
            """,
            (
                student_id,
                laptop_model,
                serial_number,
                now_ts,
                tag_uid
            )
        )
        db.commit()
    except (sqlite3.IntegrityError, db.IntegrityError):
        return jsonify({"error": "Laptop serial number already exists in the system"}), 409

    return jsonify({"message": "Gatepass successfully linked"}), 200

# Verification Helper
def _mask_name(name):
    if not name:
        return ""
    parts = name.split()
    masked_parts = []
    for part in parts:
        if len(part) <= 2:
            masked_parts.append(part[0] + "*" if len(part) == 2 else "*")
        else:
            masked_parts.append(part[0] + "*" * (len(part) - 2) + part[-1])
    return " ".join(masked_parts)

# 4. Security Guard Verification Lookup
@app.route("/api/verify/guard/<uid>", methods=["GET"])
def verify_guard(uid):
    db = get_db()
    record = db.execute(
        """
        SELECT 
            g.tag_uid,
            g.laptop_model,
            g.serial_number,
            g.is_active,
            g.registered_at,
            s.id AS student_id,
            s.student_number,
            s.full_name,
            s.phone,
            s.residence_address
        FROM gatepasses g
        LEFT JOIN students s ON g.student_id = s.id
        WHERE g.tag_uid = ?
        """,
        (uid.strip(),)
    ).fetchone()

    if not record:
        return jsonify({"error": "Invalid or unprovisioned NFC tag"}), 404

    if not record["student_id"]:
        return jsonify({
            "status": "unclaimed",
            "tag_uid": record["tag_uid"],
            "message": "Tag is provisioned but not yet linked to any student or hardware"
        }), 200

    return jsonify({
        "status": "active" if record["is_active"] else "inactive",
        "tag_uid": record["tag_uid"],
        "is_active": bool(record["is_active"]),
        "registered_at": str(record["registered_at"]) if record["registered_at"] else None,
        "hardware": {
            "laptop_model": record["laptop_model"],
            "serial_number": record["serial_number"]
        },
        "student": {
            "student_number": record["student_number"],
            "full_name": record["full_name"],
            "phone": record["phone"],
            "residence_address": record["residence_address"]
        }
    }), 200

# 5. Public / Consumer Tap Verification Lookup
@app.route("/api/verify/public/<uid>", methods=["GET"])
def verify_public(uid):
    db = get_db()
    record = db.execute(
        """
        SELECT 
            g.tag_uid,
            g.laptop_model,
            g.is_active,
            s.id AS student_id,
            s.full_name
        FROM gatepasses g
        LEFT JOIN students s ON g.student_id = s.id
        WHERE g.tag_uid = ?
        """,
        (uid.strip(),)
    ).fetchone()

    if not record:
        return jsonify({"error": "Invalid or unprovisioned NFC tag"}), 404

    if not record["student_id"]:
        return jsonify({
            "status": "unclaimed",
            "tag_uid": record["tag_uid"],
            "message": "Tag is unlinked"
        }), 200

    return jsonify({
        "status": "active" if record["is_active"] else "inactive",
        "tag_uid": record["tag_uid"],
        "is_active": bool(record["is_active"]),
        "laptop_model": record["laptop_model"],
        "student_name": _mask_name(record["full_name"])
    }), 200

# Student Registration Page
@app.route("/register", methods=["GET", "POST"])
def register_page():
    if "student_id" in session:
        return redirect(url_for("dashboard_page"))

    if request.method == "POST":
        data = request.form
        required = ["student_number", "full_name", "password", "residence_address", "phone"]
        if not all(field in data and data[field].strip() for field in required):
            return render_template("register.html", error="All fields are required.")

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
            return render_template("register.html", success="Student profile registered successfully! You can now log in.")

        except (sqlite3.IntegrityError, db.IntegrityError):
            return render_template("register.html", error="The student number is already registered.")

    return render_template("register.html")

# Admin Registry Page
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
@app.route("/login", methods=["GET", "POST"])
def login_page():
    if "student_id" in session:
        return redirect(url_for("dashboard_page"))

    if request.method == "POST":
        student_number = request.form.get("student_number", "").strip()
        password = request.form.get("password", "")

        if not student_number or not password:
            return render_template("login.html", error="Please provide both your student number and password.")

        db = get_db()
        student = db.execute(
            "SELECT * FROM students WHERE student_number = ?",
            (student_number,)
        ).fetchone()

        if not student or not check_password_hash(student["password_hash"], password):
            return render_template("login.html", error="Invalid student number or password.")

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
    student = db.execute(
        "SELECT * FROM students WHERE id = ?", (session["student_id"],)
    ).fetchone()

    if not student:
        session.clear()
        return redirect(url_for("login_page"))

    gatepass = db.execute(
        "SELECT * FROM gatepasses WHERE student_id = ?", (session["student_id"],)
    ).fetchone()

    return render_template("dashboard.html", student=student, gatepass=gatepass)

# Student Logout Handler
@app.route("/logout", methods=["GET", "POST"])
def logout_page():
    session.clear()
    return redirect(url_for("login_page"))

# Hardware Claim page and Form Handler
@app.route("/claim", methods=["GET", "POST"])
def claim_page():
    if "student_id" not in session:
        return redirect(url_for("login_page"))

    db = get_db()

    student = db.execute(
        "SELECT id FROM students WHERE id = ?", (session["student_id"],)
    ).fetchone()
    if not student:
        session.clear()
        return redirect(url_for("login_page"))

    # Prevents student with registered tags from claiming another
    existing_pass = db.execute(
        "SELECT id FROM gatepasses WHERE student_id = ?", (session["student_id"],)
    ).fetchone()

    if existing_pass:
        return redirect(url_for("dashboard_page"))

    if request.method == "POST":
        tag_uid = request.form.get("tag_uid", "").strip()
        laptop_model = request.form.get("laptop_model", "").strip()
        serial_number = request.form.get("serial_number", "").strip()

        if not tag_uid or not laptop_model or not serial_number:
            return render_template("claim.html", error="All fields are required.")

        # Check provisioned NFC tag
        tag = db.execute("SELECT * FROM gatepasses WHERE tag_uid = ?", (tag_uid,)).fetchone()

        if not tag:
            return render_template("claim.html", error="Invalid or unprovisioned NFC tag UID")

        if tag["student_id"] is not None:
            return render_template("claim.html", error="This NFC tag has already been claimed by another user")

        now_ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        try:
            db.execute(
                """
                UPDATE gatepasses
                SET student_id = ?, laptop_model = ?, serial_number = ?, registered_at = ?
                WHERE tag_uid = ?
                """,
                (
                    session["student_id"],
                    laptop_model,
                    serial_number,
                    now_ts,
                    tag_uid
                )
            )
            db.commit()
            return redirect(url_for("dashboard_page"))

        except (sqlite3.IntegrityError, db.IntegrityError):
            return render_template("claim.html", error="This laptop serial number is already registered in the system")

    return render_template("claim.html")
