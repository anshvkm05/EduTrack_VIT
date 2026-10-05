"""
EduTrack VIT — Main Flask Application
"""
import datetime
import random

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, make_response,
)
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash

from auth import login_manager, AdminUser
from database import get_db_connection

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ── App setup ─────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"] = "edutrack-vit-2025-secret"
login_manager.init_app(app)


# ── User loader ───────────────────────────────────────────────────────────
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT id, username FROM admins WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    if row:
        return AdminUser(row["id"], row["username"])
    return None


# ── Helpers ───────────────────────────────────────────────────────────────
_AVATAR_COLORS = ["blue", "violet", "green", "amber", "rose", "cyan", "indigo"]


def _avatar(name: str) -> tuple[str, str]:
    """Return (initials, color) for a student name."""
    parts = name.split()
    initials = (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()
    color = _AVATAR_COLORS[abs(hash(name)) % len(_AVATAR_COLORS)]
    return initials, color


def _enrich(rows) -> list[dict]:
    """Convert sqlite3.Row list → list of dicts with avatar info."""
    result = []
    for row in rows:
        d = dict(row)
        d["avatar"], d["color"] = _avatar(d["name"])
        d["display_id"] = f"STU-{d['id'] + 100}"
        result.append(d)
    return result


# ══════════════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════════════

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_db_connection()
        row = conn.execute(
            "SELECT id, username, password_hash FROM admins WHERE username = ?",
            (username,),
        ).fetchone()
        conn.close()
        if row and check_password_hash(row["password_hash"], password):
            login_user(AdminUser(row["id"], row["username"]), remember=True)
            return redirect(request.args.get("next") or url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "success")
    return redirect(url_for("login"))


# ══════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════

@app.route("/")
@login_required
def dashboard():
    conn = get_db_connection()
    today = datetime.date.today().isoformat()
    this_month = today[:7]

    total     = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    active    = conn.execute("SELECT COUNT(*) FROM students WHERE status='Active'").fetchone()[0]
    fees_month = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM fee_payments WHERE month = ?",
        (this_month,),
    ).fetchone()[0]

    total_att   = conn.execute("SELECT COUNT(*) FROM attendance WHERE date = ?", (today,)).fetchone()[0]
    present_att = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = ? AND present = 1", (today,)
    ).fetchone()[0]
    att_rate = round((present_att / total_att * 100) if total_att > 0 else 0)

    recent = _enrich(conn.execute("""
        SELECT s.id, s.name, c.name AS course, s.status, s.enrollment_date
        FROM students s LEFT JOIN courses c ON s.course_id = c.id
        ORDER BY s.id DESC LIMIT 5
    """).fetchall())

    conn.close()
    return render_template(
        "index.html",
        total=total, active=active,
        fees_month=fees_month, att_rate=att_rate,
        recent=recent,
    )


@app.route("/api/enrollments-by-course")
@login_required
def api_enrollments_by_course():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT c.name, COUNT(s.id) AS count
        FROM courses c LEFT JOIN students s ON s.course_id = c.id
        GROUP BY c.id ORDER BY c.name
    """).fetchall()
    conn.close()
    return jsonify({
        "labels": [r["name"] for r in rows],
        "data":   [r["count"] for r in rows],
    })


@app.route("/api/fee-trend")
@login_required
def api_fee_trend():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT month, COALESCE(SUM(amount), 0) AS total
        FROM fee_payments
        GROUP BY month ORDER BY month DESC LIMIT 6
    """).fetchall()
    conn.close()
    rows = list(reversed(rows))
    return jsonify({
        "labels": [r["month"] for r in rows],
        "data":   [r["total"] for r in rows],
    })


# ══════════════════════════════════════════════════════════════════════════
#  STUDENTS
# ══════════════════════════════════════════════════════════════════════════

def _fetch_students(search=None, status=None) -> list[dict]:
    conn = get_db_connection()
    q = """
        SELECT s.id, s.name, s.email, s.phone, s.gender,
               s.status, s.enrollment_date, c.name AS course
        FROM students s LEFT JOIN courses c ON s.course_id = c.id
        WHERE 1=1
    """
    params: list = []
    if search:
        q += " AND (s.name LIKE ? OR s.email LIKE ? OR s.phone LIKE ?)"
        params += [f"%{search}%"] * 3
    if status:
        q += " AND s.status = ?"
        params.append(status)
    q += " ORDER BY s.id DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return _enrich(rows)


@app.route("/students")
@login_required
def students():
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    roster = _fetch_students(search or None, status or None)
    return render_template("students.html", students=roster, search=search, status=status)


def _courses_and_batches():
    conn = get_db_connection()
    courses = conn.execute("SELECT id, name FROM courses ORDER BY name").fetchall()
    batches = conn.execute("""
        SELECT b.id, b.name, b.time_slot, c.name AS course, b.course_id
        FROM batches b JOIN courses c ON b.course_id = c.id
        ORDER BY c.name, b.name
    """).fetchall()
    conn.close()
    return courses, batches


@app.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():
    courses, batches = _courses_and_batches()
    if request.method == "POST":
        name      = request.form.get("name", "").strip()
        email     = request.form.get("email", "").strip()
        phone     = request.form.get("phone", "").strip()
        gender    = request.form.get("gender", "")
        course_id = request.form.get("course_id")
        batch_id  = request.form.get("batch_id")
        dob       = request.form.get("date_of_birth", "")
        status    = request.form.get("status", "Active")

        if not name or not email or not course_id:
            flash("Name, email, and course are required.", "error")
            return render_template("add_student.html", courses=courses, batches=batches)
        try:
            conn = get_db_connection()
            cur  = conn.cursor()
            cur.execute(
                "INSERT INTO students (name, email, phone, gender, course_id, date_of_birth, status) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, email, phone, gender, course_id, dob, status),
            )
            sid = cur.lastrowid
            if batch_id:
                cur.execute(
                    "INSERT OR IGNORE INTO enrollments (student_id, batch_id) VALUES (?, ?)",
                    (sid, batch_id),
                )
            conn.commit()
            conn.close()
            flash(f"{name} enrolled successfully.", "success")
            return redirect(url_for("students"))
        except Exception as exc:
            flash(f"Could not save student: {exc}", "error")
    return render_template("add_student.html", courses=courses, batches=batches)


@app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    conn = get_db_connection()
    student    = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    enrollment = conn.execute(
        "SELECT batch_id FROM enrollments WHERE student_id = ?", (student_id,)
    ).fetchone()
    conn.close()

    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("students"))

    courses, batches = _courses_and_batches()
    current_batch_id = enrollment["batch_id"] if enrollment else None

    if request.method == "POST":
        name      = request.form.get("name", "").strip()
        email     = request.form.get("email", "").strip()
        phone     = request.form.get("phone", "").strip()
        gender    = request.form.get("gender", "")
        course_id = request.form.get("course_id")
        batch_id  = request.form.get("batch_id")
        dob       = request.form.get("date_of_birth", "")
        status    = request.form.get("status", "Active")
        try:
            conn = get_db_connection()
            conn.execute(
                "UPDATE students SET name=?, email=?, phone=?, gender=?, "
                "course_id=?, date_of_birth=?, status=? WHERE id=?",
                (name, email, phone, gender, course_id, dob, status, student_id),
            )
            conn.execute("DELETE FROM enrollments WHERE student_id = ?", (student_id,))
            if batch_id:
                conn.execute(
                    "INSERT OR IGNORE INTO enrollments (student_id, batch_id) VALUES (?, ?)",
                    (student_id, batch_id),
                )
            conn.commit()
            conn.close()
            flash(f"{name} updated successfully.", "success")
            return redirect(url_for("students"))
        except Exception as exc:
            flash(f"Could not update student: {exc}", "error")

    return render_template(
        "edit_student.html",
        student=dict(student),
        courses=courses, batches=batches,
        current_batch_id=current_batch_id,
    )


@app.route("/students/<int:student_id>/delete", methods=["POST"])
@login_required
def delete_student(student_id):
    conn = get_db_connection()
    row  = conn.execute("SELECT name FROM students WHERE id = ?", (student_id,)).fetchone()
    if row:
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        flash(f"{row['name']} has been removed.", "success")
    conn.close()
    return redirect(url_for("students"))


@app.route("/students/<int:student_id>/report.pdf")
@login_required
def student_pdf(student_id):
    if not PDF_AVAILABLE:
        flash("fpdf2 is not installed. Run: pip install fpdf2", "error")
        return redirect(url_for("students"))

    conn = get_db_connection()
    s = conn.execute("""
        SELECT s.*, c.name AS course
        FROM students s LEFT JOIN courses c ON s.course_id = c.id
        WHERE s.id = ?
    """, (student_id,)).fetchone()
    fees = conn.execute(
        "SELECT * FROM fee_payments WHERE student_id = ? ORDER BY month DESC",
        (student_id,),
    ).fetchall()
    conn.close()

    if not s:
        flash("Student not found.", "error")
        return redirect(url_for("students"))

    pdf = FPDF()
    pdf.add_page()

    # ── Header band ──
    pdf.set_fill_color(17, 24, 39)
    pdf.rect(0, 0, 210, 42, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(0, 8)
    pdf.cell(210, 12, "EduTrack VIT", align="C", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(210, 8, "Student Report Card", align="C", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(12)

    # ── Student Details ──
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, s["name"], ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 90, 110)
    pdf.cell(0, 6, f"Student ID: STU-{s['id'] + 100}  |  Status: {s['status']}", ln=True)
    pdf.ln(4)

    pdf.set_draw_color(200, 210, 230)
    pdf.set_line_width(0.3)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    info = [
        ("Course",          s["course"] or "N/A"),
        ("Email",           s["email"]),
        ("Phone",           s["phone"] or "N/A"),
        ("Gender",          s["gender"] or "N/A"),
        ("Date of Birth",   s["date_of_birth"] or "N/A"),
        ("Enrollment Date", s["enrollment_date"] or "N/A"),
    ]
    pdf.set_text_color(0, 0, 0)
    for label, value in info:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(55, 7, label + ":", border=0)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, str(value), ln=True)

    pdf.ln(8)

    # ── Fee history ──
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 9, "Fee Payment History", ln=True)

    pdf.set_fill_color(235, 240, 255)
    pdf.set_font("Helvetica", "B", 9)
    for col, w in [("Month", 38), ("Amount (Rs.)", 38), ("Paid On", 40), ("Note", 74)]:
        pdf.cell(w, 8, col, border=1, fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    total_paid = 0
    for f in fees:
        pdf.cell(38, 7, f["month"],          border=1)
        pdf.cell(38, 7, f"Rs. {int(f['amount'])}", border=1)
        pdf.cell(40, 7, f["paid_on"] or "-", border=1)
        pdf.cell(74, 7, f["note"]    or "-", border=1)
        pdf.ln()
        total_paid += f["amount"]

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(76, 8, "Total Paid", border=1)
    pdf.cell(0,  8, f"Rs. {int(total_paid)}", border=1, ln=True)

    # ── Footer ──
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(140, 150, 170)
    pdf.cell(0, 6, f"Generated by EduTrack VIT  ·  {datetime.date.today().isoformat()}", align="C")

    response = make_response(bytes(pdf.output()))
    response.headers["Content-Type"] = "application/pdf"
    safe_name = s["name"].replace(" ", "_")
    response.headers["Content-Disposition"] = f'attachment; filename="EduTrack_{safe_name}.pdf"'
    return response


# ══════════════════════════════════════════════════════════════════════════
#  FEE PAYMENTS
# ══════════════════════════════════════════════════════════════════════════

@app.route("/fees")
@login_required
def fees():
    month = request.args.get("month", datetime.date.today().strftime("%Y-%m"))
    conn  = get_db_connection()
    records = conn.execute("""
        SELECT f.id, f.amount, f.month, f.paid_on, f.note,
               s.name AS student_name, c.name AS course
        FROM fee_payments f
        JOIN students s ON f.student_id = s.id
        LEFT JOIN courses c ON s.course_id = c.id
        WHERE f.month = ?
        ORDER BY f.paid_on DESC, s.name
    """, (month,)).fetchall()
    total = sum(r["amount"] for r in records)
    conn.close()
    return render_template("fees.html", records=records, total=total, month=month)


@app.route("/fees/add", methods=["GET", "POST"])
@login_required
def add_fee():
    conn          = get_db_connection()
    students_list = conn.execute(
        "SELECT id, name FROM students WHERE status='Active' ORDER BY name"
    ).fetchall()
    conn.close()

    default_month = datetime.date.today().strftime("%Y-%m")

    if request.method == "POST":
        student_id = request.form.get("student_id")
        amount     = request.form.get("amount")
        month      = request.form.get("month", default_month)
        note       = request.form.get("note", "").strip()
        paid_on    = datetime.date.today().isoformat()

        if not student_id or not amount or not month:
            flash("Student, amount, and month are required.", "error")
            return render_template("add_fee.html", students=students_list, default_month=default_month)
        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO fee_payments (student_id, amount, month, paid_on, note) "
                "VALUES (?, ?, ?, ?, ?)",
                (student_id, float(amount), month, paid_on, note),
            )
            conn.commit()
            conn.close()
            flash("Payment recorded successfully.", "success")
            return redirect(url_for("fees", month=month))
        except Exception as exc:
            flash(f"Could not save payment: {exc}", "error")

    return render_template("add_fee.html", students=students_list, default_month=default_month)


# ══════════════════════════════════════════════════════════════════════════
#  ATTENDANCE
# ══════════════════════════════════════════════════════════════════════════

@app.route("/attendance")
@login_required
def attendance():
    today    = datetime.date.today().isoformat()
    att_date = request.args.get("date", today)
    batch_id = request.args.get("batch_id", "")

    conn    = get_db_connection()
    batches = conn.execute("""
        SELECT b.id, b.name, b.time_slot, c.name AS course
        FROM batches b JOIN courses c ON b.course_id = c.id
        ORDER BY c.name, b.name
    """).fetchall()

    student_list = []
    batch_name   = ""
    if batch_id:
        batch_row = conn.execute("SELECT name FROM batches WHERE id = ?", (batch_id,)).fetchone()
        batch_name = batch_row["name"] if batch_row else ""
        student_list = conn.execute("""
            SELECT s.id, s.name,
                   COALESCE(
                       (SELECT present FROM attendance
                        WHERE student_id = s.id AND batch_id = ? AND date = ?),
                       -1
                   ) AS present
            FROM students s
            JOIN enrollments e ON e.student_id = s.id
            WHERE e.batch_id = ? AND s.status = 'Active'
            ORDER BY s.name
        """, (batch_id, att_date, batch_id)).fetchall()

    conn.close()
    return render_template(
        "attendance.html",
        batches=batches,
        students=student_list,
        date=att_date, today=today,
        batch_id=batch_id, batch_name=batch_name,
    )


@app.route("/attendance/mark", methods=["POST"])
@login_required
def mark_attendance():
    att_date    = request.form.get("date")
    batch_id    = request.form.get("batch_id")
    present_ids = set(request.form.getlist("present"))

    conn = get_db_connection()
    all_students = conn.execute("""
        SELECT s.id FROM students s
        JOIN enrollments e ON e.student_id = s.id
        WHERE e.batch_id = ? AND s.status = 'Active'
    """, (batch_id,)).fetchall()

    for row in all_students:
        is_present = 1 if str(row["id"]) in present_ids else 0
        conn.execute(
            "INSERT OR REPLACE INTO attendance (student_id, batch_id, date, present) "
            "VALUES (?, ?, ?, ?)",
            (row["id"], batch_id, att_date, is_present),
        )
    conn.commit()
    conn.close()
    flash(f"Attendance saved for {att_date}.", "success")
    return redirect(url_for("attendance", date=att_date, batch_id=batch_id))


# ══════════════════════════════════════════════════════════════════════════
#  BATCHES
# ══════════════════════════════════════════════════════════════════════════

@app.route("/batches")
@login_required
def batches():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT b.id, b.name, b.time_slot, c.name AS course,
               COUNT(e.student_id) AS student_count
        FROM batches b
        JOIN courses c ON b.course_id = c.id
        LEFT JOIN enrollments e ON e.batch_id = b.id
        GROUP BY b.id ORDER BY c.name, b.name
    """).fetchall()
    conn.close()
    return render_template("batches.html", batches=rows)


@app.route("/batches/add", methods=["GET", "POST"])
@login_required
def add_batch():
    conn    = get_db_connection()
    courses = conn.execute("SELECT id, name FROM courses ORDER BY name").fetchall()
    conn.close()

    if request.method == "POST":
        name      = request.form.get("name", "").strip()
        course_id = request.form.get("course_id")
        time_slot = request.form.get("time_slot", "").strip()
        if not name or not course_id:
            flash("Batch name and course are required.", "error")
            return render_template("add_batch.html", courses=courses)
        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO batches (name, course_id, time_slot) VALUES (?, ?, ?)",
                (name, course_id, time_slot),
            )
            conn.commit()
            conn.close()
            flash(f"Batch '{name}' created successfully.", "success")
            return redirect(url_for("batches"))
        except Exception as exc:
            flash(f"Could not create batch: {exc}", "error")

    return render_template("add_batch.html", courses=courses)


# ══════════════════════════════════════════════════════════════════════════
#  ABOUT
# ══════════════════════════════════════════════════════════════════════════

@app.route("/about")
@login_required
def about():
    return render_template("about.html")


# ── Entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
