from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            role TEXT,
            location TEXT,
            applied_date TEXT,
            status TEXT,
            job_url TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/applications/add", methods=["GET", "POST"])
def add_application():
    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        applied_date = request.form["applied_date"]
        status = request.form["status"]
        job_url = request.form["job_url"]
        notes = request.form["notes"]

        conn = sqlite3.connect("jobs.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO applications (company, role, location, applied_date, status, job_url, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (company, role, location, applied_date, status, job_url, notes)
        )
        conn.commit()
        conn.close()

        return redirect("/applications")

    return render_template("add_application.html")



@app.route("/applications/<int:app_id>/delete")
def delete_application(app_id):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    conn.commit()
    conn.close()
    return redirect("/applications")

@app.route("/applications/<int:app_id>/edit", methods=["GET", "POST"])
def edit_application(app_id):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        applied_date = request.form["applied_date"]
        status = request.form["status"]
        job_url = request.form["job_url"]
        notes = request.form["notes"]

        cursor.execute("""
            UPDATE applications
            SET company = ?, role = ?, location = ?, applied_date = ?, status = ?, job_url = ?, notes = ?
            WHERE id = ?
        """, (company, role, location, applied_date, status, job_url, notes, app_id))
        conn.commit()
        conn.close()
        return redirect("/applications")

    cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
    application = cursor.fetchone()
    conn.close()
    return render_template("edit_application.html", application=application)
@app.route("/statistics")
def statistics():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM applications")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT status, COUNT(*) FROM applications GROUP BY status")
    status_counts = cursor.fetchall()

    conn.close()

    return render_template("statistics.html", total=total, status_counts=status_counts)

@app.route("/applications")
def view_applications():
    search = request.args.get("search", "")
    status_filter = request.args.get("status", "")

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    query = "SELECT * FROM applications WHERE company LIKE ?"
    params = ["%" + search + "%"]

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return render_template("applications.html", applications=rows, search=search, status_filter=status_filter)

if __name__ == "__main__":
    app.run(debug=True)