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
