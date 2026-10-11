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
* Link their laptop hardware to an issued NFC tag via the dedicated `/claim` portal

### Administrator Portal

Administrators can access a centralized directory containing:

* Registered students
* Active NFC tag UIDs
* Assigned laptop models
* Registered hardware information

## Project Structure

```text
NFC_gatepass/
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
│   ├── claim.html          # NFC tag and hardware registration page
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
git clone https://github.com/NeoA231/NFC_gatepass.git
cd NFC_gatepass
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
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
| `/register`                | `GET`, `POST` | Student account registration portal                            |
| `/login`                   | `GET`, `POST` | Student login portal                                           |
| `/logout`                  | `GET`, `POST` | Student session logout                                         |
| `/dashboard`               | `GET`         | Authenticated student dashboard showing linked gatepass status |
| `/claim`                   | `GET`, `POST` | In-browser hardware and NFC tag linking interface              |
| `/admin/students`          | `GET`         | Administrator registry containing students and tags            |
| `/api/register`            | `POST`        | REST API: Student profile registration                         |
| `/api/tags/provision`      | `POST`        | REST API: Registers a blank NFC tag UID                        |
| `/api/gatepass/claim`      | `POST`        | REST API: Links student & laptop serial to an NFC tag UID      |
| `/api/verify/guard/<uid>`  | `GET`         | Security guard verification lookup                             |
| `/api/verify/public/<uid>` | `GET`         | Public verification endpoint with masked student information   |

## Planned Roadmap

* [x] Build the in-browser `/claim` interface for students
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

The project is currently under development. The core Flask application, database structure, student authentication, hardware claiming portal, and verification endpoints are operational.
