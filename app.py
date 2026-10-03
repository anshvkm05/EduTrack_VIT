from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)
from database import get_db_connection

app = Flask(__name__)
app.config["SECRET_KEY"] = "studenthub-local-development"


def fetch_students(limit=None):
    query = """
        SELECT CONCAT('STU-', id + 100) AS id, name, course, status,
               UPPER(CONCAT(LEFT(SUBSTRING_INDEX(name, ' ', 1), 1),
                            LEFT(SUBSTRING_INDEX(name, ' ', -1), 1))) AS avatar
        FROM students
        ORDER BY id DESC
    """
    if limit:
        query += " LIMIT %s"

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, (limit,) if limit else ())
        students = cursor.fetchall()
        for student in students:
            student["color"] = "blue"
        return students
    finally:
        cursor.close()
        connection.close()


@app.route("/")
def home():
    try:
        students = fetch_students(limit=3)
        total_students = len(fetch_students())
    except Error:
        students, total_students = [], 0
        flash("MySQL is not connected yet. Run setup_database.py after configuring .env.", "error")
    return render_template("index.html", students=students, total_students=total_students)


@app.route("/students")
def students():
    try:
        roster = fetch_students()
    except Error:
        roster = []
        flash("MySQL is not connected yet. Run setup_database.py after configuring .env.", "error")
    return render_template("students.html", students=roster)


@app.route("/students/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        course = request.form.get("course", "").strip()
        status = request.form.get("status", "Active")

        if not name or not course:
            flash("Enter a student name and course.", "error")
            return render_template("add_student.html")

        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO students (name, course, status) VALUES (%s, %s, %s)",
                (name, course, status),
            )
            connection.commit()
            cursor.close()
            connection.close()
        except Error:
            flash("Student could not be saved because MySQL is not connected.", "error")
            return render_template("add_student.html")

        flash(f"{name} was added successfully.", "success")
        return redirect(url_for("students"))

    return render_template("add_student.html")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
