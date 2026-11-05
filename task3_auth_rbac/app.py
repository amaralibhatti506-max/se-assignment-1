import datetime
import os
import sqlite3
from functools import wraps

import jwt
from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me-in-production-32b")
DB = os.environ.get("DB_PATH", "employees.db")


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY, password_hash TEXT NOT NULL, role TEXT NOT NULL)"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, position TEXT NOT NULL, salary REAL NOT NULL)"""
        )
        if not conn.execute("SELECT 1 FROM users").fetchone():
            conn.executemany(
                "INSERT INTO users VALUES (?,?,?)",
                [
                    ("admin", generate_password_hash("admin123"), "admin"),
                    ("employee", generate_password_hash("emp123"), "employee"),
                ],
            )
            conn.execute("INSERT INTO employees (name, position, salary) VALUES ('Ali Khan','Developer',120000)")
            conn.execute("INSERT INTO employees (name, position, salary) VALUES ('Sara Ahmed','Designer',100000)")


# ---------- Authentication ----------
def authenticated(fn):
    """401 if no valid token."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "Authentication required. Login at POST /login."}), 401
        try:
            payload = jwt.decode(header[7:], app.config["SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        request.user = payload
        return fn(*args, **kwargs)

    return wrapper


# ---------- Authorization ----------
def roles_required(*roles):
    """403 if authenticated but role not allowed."""
    def decorator(fn):
        @wraps(fn)
        @authenticated
        def wrapper(*args, **kwargs):
            if request.user["role"] not in roles:
                return jsonify({"error": "Forbidden: insufficient permissions"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE username=?", (data.get("username"),)).fetchone()
    if not user or not check_password_hash(user["password_hash"], data.get("password") or ""):
        return jsonify({"error": "Invalid credentials"}), 401
    token = jwt.encode(
        {
            "sub": user["username"],
            "role": user["role"],
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
        },
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )
    return jsonify({"token": token, "role": user["role"]})


def emp_data():
    d = request.get_json(silent=True) or {}
    try:
        return str(d["name"]).strip(), str(d["position"]).strip(), float(d["salary"])
    except (KeyError, ValueError):
        return None


@app.get("/employees")
@roles_required("employee", "admin")
def list_employees():
    with get_db() as conn:
        return jsonify([dict(r) for r in conn.execute("SELECT * FROM employees")])


@app.get("/employees/<int:eid>")
@roles_required("employee", "admin")
def get_employee(eid):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM employees WHERE id=?", (eid,)).fetchone()
    return (jsonify(dict(row)), 200) if row else (jsonify({"error": "Not found"}), 404)


@app.post("/employees")
@roles_required("admin")
def add_employee():
    d = emp_data()
    if not d:
        return jsonify({"error": "name, position, salary required"}), 400
    with get_db() as conn:
        cur = conn.execute("INSERT INTO employees (name, position, salary) VALUES (?,?,?)", d)
    return jsonify({"id": cur.lastrowid, "name": d[0], "position": d[1], "salary": d[2]}), 201


@app.put("/employees/<int:eid>")
@roles_required("admin")
def update_employee(eid):
    d = emp_data()
    if not d:
        return jsonify({"error": "name, position, salary required"}), 400
    with get_db() as conn:
        cur = conn.execute("UPDATE employees SET name=?, position=?, salary=? WHERE id=?", (*d, eid))
    return (jsonify({"message": "Updated"}), 200) if cur.rowcount else (jsonify({"error": "Not found"}), 404)


@app.delete("/employees/<int:eid>")
@roles_required("admin")
def delete_employee(eid):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM employees WHERE id=?", (eid,))
    return (jsonify({"message": "Deleted"}), 200) if cur.rowcount else (jsonify({"error": "Not found"}), 404)


init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5002)
