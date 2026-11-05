import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB = "students.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )"""
        )


def validate(data, require_all=True):
    if not data:
        return "JSON body required"
    for f in ("name", "department", "email"):
        if require_all and not str(data.get(f, "")).strip():
            return f"'{f}' is required"
    return None


@app.get("/students")
def get_students():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM students ORDER BY id").fetchall()
    return jsonify([dict(r) for r in rows])


@app.get("/students/<int:sid>")
def get_student(sid):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
    if not row:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(dict(row))


@app.post("/students")
def add_student():
    data = request.get_json(silent=True)
    err = validate(data)
    if err:
        return jsonify({"error": err}), 400
    try:
        with get_db() as conn:
            cur = conn.execute(
                "INSERT INTO students (name, department, email) VALUES (?,?,?)",
                (data["name"].strip(), data["department"].strip(), data["email"].strip()),
            )
            sid = cur.lastrowid
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    return jsonify({"id": sid, **{k: data[k] for k in ("name", "department", "email")}}), 201


@app.put("/students/<int:sid>")
def update_student(sid):
    data = request.get_json(silent=True)
    err = validate(data)
    if err:
        return jsonify({"error": err}), 400
    try:
        with get_db() as conn:
            cur = conn.execute(
                "UPDATE students SET name=?, department=?, email=? WHERE id=?",
                (data["name"].strip(), data["department"].strip(), data["email"].strip(), sid),
            )
            if cur.rowcount == 0:
                return jsonify({"error": "Student not found"}), 404
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    return jsonify({"message": "Student updated"})


@app.delete("/students/<int:sid>")
def delete_student(sid):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM students WHERE id=?", (sid,))
        if cur.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404
    return jsonify({"message": "Student deleted"})


init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
