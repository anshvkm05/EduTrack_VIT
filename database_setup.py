"""
EduTrack VIT — Database Setup
Creates all tables and seeds sample data.
Run: python database_setup.py
"""

import datetime
import random
from database import get_db_connection
from werkzeug.security import generate_password_hash

conn = get_db_connection()
c = conn.cursor()

# ── Drop old tables (clean slate) ──────────────────────────────────────────
c.executescript("""
    PRAGMA foreign_keys = OFF;
    DROP TABLE IF EXISTS attendance;
    DROP TABLE IF EXISTS fee_payments;
    DROP TABLE IF EXISTS enrollments;
    DROP TABLE IF EXISTS students;
    DROP TABLE IF EXISTS batches;
    DROP TABLE IF EXISTS courses;
    DROP TABLE IF EXISTS admins;
    PRAGMA foreign_keys = ON;
""")

# ── Create tables ──────────────────────────────────────────────────────────
c.executescript("""
    CREATE TABLE admins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT    NOT NULL UNIQUE,
        password_hash TEXT    NOT NULL
    );

    CREATE TABLE courses (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT    NOT NULL UNIQUE
    );

    CREATE TABLE batches (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        name      TEXT    NOT NULL,
        course_id INTEGER NOT NULL,
        time_slot TEXT,
        FOREIGN KEY (course_id) REFERENCES courses(id)
    );

    CREATE TABLE students (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT    NOT NULL,
        email           TEXT    NOT NULL UNIQUE,
        phone           TEXT,
        gender          TEXT,
        course_id       INTEGER NOT NULL,
        date_of_birth   TEXT,
        enrollment_date TEXT    DEFAULT CURRENT_DATE,
        status          TEXT    NOT NULL DEFAULT 'Active',
        FOREIGN KEY (course_id) REFERENCES courses(id)
    );

    CREATE TABLE enrollments (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        batch_id   INTEGER NOT NULL,
        UNIQUE(student_id, batch_id),
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY (batch_id)   REFERENCES batches(id)
    );

    CREATE TABLE fee_payments (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        amount     REAL    NOT NULL,
        month      TEXT    NOT NULL,
        paid_on    TEXT,
        note       TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );

    CREATE TABLE attendance (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        batch_id   INTEGER NOT NULL,
        date       TEXT    NOT NULL,
        present    INTEGER NOT NULL DEFAULT 0,
        UNIQUE(student_id, batch_id, date),
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY (batch_id)   REFERENCES batches(id)
    );
""")

# ── Seed: admin ────────────────────────────────────────────────────────────
c.execute(
    "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
    ("admin", generate_password_hash("admin123")),
)

# ── Seed: courses ──────────────────────────────────────────────────────────
courses = [("BCA",), ("BSc IT",), ("MCA",), ("BTech CS",)]
c.executemany("INSERT INTO courses (name) VALUES (?)", courses)
# IDs: BCA=1, BSc IT=2, MCA=3, BTech CS=4

# ── Seed: batches ──────────────────────────────────────────────────────────
batches = [
    ("BCA Morning",       1, "8:00 AM – 10:00 AM"),
    ("BCA Evening",       1, "5:00 PM – 7:00 PM"),
    ("BSc IT Morning",    2, "9:00 AM – 11:00 AM"),
    ("BSc IT Evening",    2, "4:00 PM – 6:00 PM"),
    ("MCA Afternoon",     3, "2:00 PM – 4:00 PM"),
    ("BTech CS Morning",  4, "7:30 AM – 9:30 AM"),
    ("BTech CS Weekend",  4, "Sat–Sun 10:00 AM – 1:00 PM"),
]
c.executemany("INSERT INTO batches (name, course_id, time_slot) VALUES (?, ?, ?)", batches)
# IDs: 1..7

# ── Seed: students ─────────────────────────────────────────────────────────
students = [
    ("Rahul Sharma",  "rahul.sharma@vit.ac.in",  "9876543210", "Male",   1, "2002-04-12", "2025-06-15", "Active"),
    ("Ayesha Khan",   "ayesha.khan@vit.ac.in",   "9123456789", "Female", 2, "2003-08-21", "2025-06-18", "Active"),
    ("Arjun Mehta",   "arjun.mehta@vit.ac.in",   "9988776655", "Male",   1, "2002-11-10", "2025-06-20", "Active"),
    ("Emily Davis",   "emily.davis@vit.ac.in",   "9876501234", "Female", 4, "2001-05-14", "2025-06-22", "Inactive"),
    ("Chris Wilson",  "chris.wilson@vit.ac.in",  "9765432109", "Male",   3, "2002-01-25", "2025-06-25", "Active"),
    ("Sara Patel",    "sara.patel@vit.ac.in",    "9898989898", "Female", 2, "2003-03-17", "2025-07-01", "Active"),
    ("Kabir Shah",    "kabir.shah@vit.ac.in",    "9000011111", "Male",   3, "2002-09-09", "2025-07-03", "Inactive"),
    ("Maya Thomas",   "maya.thomas@vit.ac.in",   "9888877777", "Female", 4, "2001-12-04", "2025-07-05", "Active"),
    ("Priya Nair",    "priya.nair@vit.ac.in",    "9111222333", "Female", 1, "2003-06-18", "2025-07-10", "Active"),
    ("Rohan Verma",   "rohan.verma@vit.ac.in",   "9444555666", "Male",   4, "2002-03-25", "2025-07-12", "Active"),
]
c.executemany(
    "INSERT INTO students (name, email, phone, gender, course_id, date_of_birth, enrollment_date, status) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    students,
)
# IDs: 1..10

# ── Seed: enrollments ─────────────────────────────────────────────────────
# student_id → batch_id
enrollments = [
    (1, 1),   # Rahul   → BCA Morning
    (2, 3),   # Ayesha  → BSc IT Morning
    (3, 2),   # Arjun   → BCA Evening
    (4, 6),   # Emily   → BTech CS Morning
    (5, 5),   # Chris   → MCA Afternoon
    (6, 4),   # Sara    → BSc IT Evening
    (7, 5),   # Kabir   → MCA Afternoon
    (8, 7),   # Maya    → BTech CS Weekend
    (9, 1),   # Priya   → BCA Morning
    (10, 7),  # Rohan   → BTech CS Weekend
]
c.executemany("INSERT INTO enrollments (student_id, batch_id) VALUES (?, ?)", enrollments)

# ── Seed: fee payments (last 4 months) ─────────────────────────────────────
today = datetime.date.today()
months = [
    (today.replace(day=1) - datetime.timedelta(days=30 * i)).strftime("%Y-%m")
    for i in range(4)
]
random.seed(42)
active_students = [1, 2, 3, 5, 6, 8, 9, 10]
fee_records = []
for month in months:
    for sid in active_students:
        # ~80% payment rate for realism
        if random.random() < 0.8:
            fee_records.append((sid, 5000, month, today.isoformat(), "Monthly tuition fee"))
c.executemany(
    "INSERT INTO fee_payments (student_id, amount, month, paid_on, note) VALUES (?, ?, ?, ?, ?)",
    fee_records,
)

# ── Seed: attendance (last 7 days for two batches) ─────────────────────────
batch_students = {
    1: [1, 9],   # BCA Morning → Rahul, Priya
    5: [5, 7],   # MCA Afternoon → Chris, Kabir
}
for i in range(7):
    att_date = (today - datetime.timedelta(days=i)).isoformat()
    for batch_id, sids in batch_students.items():
        for sid in sids:
            present = 1 if random.random() > 0.25 else 0
            c.execute(
                "INSERT OR IGNORE INTO attendance (student_id, batch_id, date, present) VALUES (?, ?, ?, ?)",
                (sid, batch_id, att_date, present),
            )

conn.commit()
conn.close()
print("EduTrack VIT database setup completed successfully.")
print("Login: admin / admin123")
