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
