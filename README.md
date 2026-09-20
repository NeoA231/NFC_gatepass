# NFC-Based Student Laptop Gatepass System

A lightweight web application built with **Flask** and **SQLite** to replace fragile three-month paper gatepass receipts with programmed **Near Field Communication (NFC)** tags.

The system binds a student profile and laptop hardware serial number to an individual physical NFC tag UID. Security guards can tap the tag to rapidly verify physical hardware against a centralized registry without requiring a password, while public device scans restrict sensitive owner information.

## Features

### Centralized Registry

Eliminates forged physical receipts by matching physical laptop serial numbers directly against database records.

### Two-Tier Access Verification

* **Security Checkpoint**

  * Fast, read-only lookup
  * Displays student verification information
  * Displays registered laptop hardware specifications
  * Does not require student authentication

* **Public / Consumer Tap**

  * Masks sensitive student identity information
  * Conceals hardware serial numbers
  * Provides limited verification information
  * Designed for scans performed by people other than security staff

### Student Self-Service

Students can:

* Register an account
* Log into a session-backed dashboard
* View their gatepass information
* Link their laptop hardware to an issued NFC tag

### Administrator Portal

Administrators can access a centralized directory containing:

* Registered students
* Active NFC tag UIDs
* Assigned laptop models
* Registered hardware information

## Project Structure

```text
nfc-gatepass/
│
├── app.py                  # Flask application routes, session handling, and APIs
│
├── db/
│   ├── database.py         # SQLite connection helpers and database initialization
│   └── schema.sql          # Relational database schema and table definitions
│
├── templates/
│   ├── register.html       # Student registration page
│   ├── login.html          # Authentication portal
│   ├── dashboard.html      # Protected student dashboard
│   └── admin_students.html # Administrator student and hardware overview
│
└── README.md
```

## Database Architecture

The system uses **SQLite** with enforced foreign key constraints.

### `students`

Stores student account and identity information, including:

* Student details
* Hashed credentials
* Phone numbers
* Residence addresses

### `gatepasses`

Stores gatepass and hardware information, including:

* NFC tag UIDs
* Associated student IDs
* Laptop specifications
* Unique hardware serial numbers

## Local Setup

### Windows

### 1. Clone the Repository

Open PowerShell and run:

```powershell
git clone https://github.com/<your-username>/nfc-gatepass.git
cd nfc-gatepass
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install Dependencies

```powershell
pip install Flask werkzeug
```

### 4. Initialize the SQLite Database

Set the Flask application and run the custom database initialization command:

```powershell
$env:FLASK_APP = "app.py"
flask init-db
```

### 5. Start the Development Server

```powershell
flask run --debug --port 5000
```

The application will be available at:

http://127.0.0.1:5000

## Key Endpoints

| Route                      | Method        | Description                                                    |
| -------------------------- | ------------- | -------------------------------------------------------------- |
| `/register`                | `GET`, `POST` | Student account registration                                   |
| `/login`                   | `GET`, `POST` | Student login portal                                           |
| `/dashboard`               | `GET`         | Authenticated student dashboard showing linked gatepass status |
| `/admin/students`          | `GET`         | Administrator registry containing students and tags            |
| `/api/tags/provision`      | `POST`        | Registers a blank NFC tag UID                                  |
| `/api/gatepass/claim`      | `POST`        | Links a student and laptop serial number to an NFC tag UID     |
| `/api/verify/guard/<uid>`  | `GET`         | Security guard verification lookup                             |
| `/api/verify/public/<uid>` | `GET`         | Public verification endpoint with masked student information   |

## Planned Roadmap

* [ ] Build the in-browser `/claim` interface for students
* [ ] Upgrade the storage layer from SQLite to a dedicated SQL server such as PostgreSQL or MySQL
* [ ] Deploy to a personal Linux server
* [ ] Configure Nginx as a reverse proxy
* [ ] Deploy the Flask application using Gunicorn

## Technology Stack

| Technology   | Purpose                              |
| ------------ | ------------------------------------ |
| **Python**   | Application programming language     |
| **Flask**    | Web application framework            |
| **SQLite**   | Database                             |
| **Jinja2**   | Frontend templating                  |
| **NFC**      | Physical gatepass identification     |
| **Werkzeug** | Password hashing and Flask utilities |

## Project Status

The project is currently under development. The core Flask application, database structure, student authentication, gatepass management, and verification endpoints are being developed as part of the NFC-based student laptop gatepass system.
