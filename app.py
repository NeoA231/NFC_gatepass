from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from db.database import get_db, close_db, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = "qwertyBOARD" #"replace-this-with-random-secret-key"

app.teardown_appcontext(close_db)

@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("Initialised the SQLite database.")

# 1. Student Regiastration
@app.route("api/register", methods=['POST'])
def register():
    data = request.get_json() or {}
    required = ['student_number', 'full_name', 'password', 'residence_address']
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
        return jsonify({'error': "Student number already registered"}),400

    return jsonify({'message': 'Student registered successfully', "student_id": cursor.lastrowid}), 201

# 2. Tag Provisioning
@app.route("/api/tags/provision", methods=["POST"])
def provision_tag():
    data = request.get_jason() or {}
    tag_uid = data.get("tag_uid")
    if not tag_uid:
        return jsonify({"error": "tag_uid required"}), 400

    db = get_db()
    try:
        db.execute('ISERT INTO gatepasses (tag_uid) VALUES (?)', (tag_uid))
        db.commit()
    except db.IntegrityError:
        return jsonify({"error" : "Tag already provisioned"}), 409

    return jsonify({"message": "Tag provisioned with null data", "tag_uid": tag_uid}),201


# 3. Laptop registration
@app.route("/api/gatepass/claim")
def claim_tag():
    data = request.get_jason() or {}
    required = ["tag_uid", "student_id", "laptop_model", "serial_number"]

    if not all(field in data for field in required):
        return jsonify({"error": "Missing hardware registration fields"}), 400

    db =get_db()
    tag = db.execute("SELECT * FROM gatepasses WHERE tag_uid = ?", (data["tag_uid"],)).fetchone()

    if not tag:
        return jsonify({"error": "Invalid or unprovisioned NFC tag"}), 404
    if tag["student_id"] is not None:
        return jsonify({"error": "Tag has been claimed"}), 409
    try:
        db.execute(
            """
            UPDATE gatepasses
            SET student_id = ?, laptop_model = ?, registered_at = ?
            """,
            (data["student_id"], data["laptop_model"], data["serial_number"], datetime.datetime.utcnow(), data["tag_uid"])
            )
        db.commit()
    except db.IntegrityError:
        return jsonify({"error": "Laptop serial number already exist in system"}), 409

    return jsonify({"message": "Gatepass successfully linked"}), 200

