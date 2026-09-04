PRAGMA foreign_key = ON;

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_number TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    phone TEXT NOT NULL,
    residence_address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS  gatepasses(
    id INTEGERF PRIMARY KEY AUTOINCREMENT,
    tag_uid TEXT UNIQUE NOT NULL,
    student_id INTEGEER,
    serial_number TEXT UNIQUE, 
    is_active INTEGER DEFAULT 1,
    registered_at TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTSidx_gatepass_tag ON gatepasses(tag_uid);
CREATE INDEX IF NOT EXISTS idx_student_number ON students(student_number);