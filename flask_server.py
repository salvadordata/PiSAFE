from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
import sqlite3
import subprocess
from mqtt_client import forward_alert, send_notifications
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Environment Variables for Secure Configurations
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "default_secret_key")
DEBUG_MODE = os.getenv("FLASK_DEBUG", "false").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

app.secret_key = FLASK_SECRET_KEY

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


class User(UserMixin):
    pass


# Database functions
def query_db(query, args=(), one=False):
    """
    Executes a query on the database and returns the result.
    """
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv


def modify_db(query, args=()):
    """
    Executes a modification query on the database (INSERT/UPDATE/DELETE).
    """
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    conn.close()


@login_manager.user_loader
def user_loader(username):
    """
    Loads a user by username.
    """
    user_record = query_db(
        "SELECT username, role FROM users WHERE username = ?", [username], one=True
    )
    if user_record is None:
        return None
    user = User()
    user.id = user_record[0]
    user.role = user_record[1]
    return user


@app.before_request
def enforce_https():
    """
    Enforce HTTPS in production environment.
    """
    if ENVIRONMENT == "production" and not request.is_secure:
        return jsonify({"error": "HTTPS is required in production"}), 403


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles user login.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_record = query_db(
            "SELECT username, password, role FROM users WHERE username = ?",
            [username],
            one=True,
        )
        if user_record and check_password_hash(user_record[1], password):
            user = User()
            user.id = user_record[0]
            user.role = user_record[2]
            login_user(user)
            return redirect(url_for("index"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """
    Logs the current user out.
    """
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    """
    Displays the main dashboard.
    """
    alerts_count = query_db("SELECT COUNT(*) FROM logs", one=True)[0]
    user_count = query_db("SELECT COUNT(*) FROM users", one=True)[0]
    system_uptime = (
        datetime.now()
        - datetime.fromtimestamp(
            query_db("SELECT MIN(timestamp) FROM logs", one=True)[0]
        )
    ).total_seconds()
    return render_template(
        "index.html",
        role=current_user.role,
        alerts_count=alerts_count,
        user_count=user_count,
        system_uptime=system_uptime,
    )


@app.route("/trigger", methods=["POST"])
@login_required
def trigger_alert():
    """
    Triggers an emergency alert.
    """
    if current_user.role != "admin":
        flash("You do not have permission to perform this action", "danger")
        return redirect(url_for("index"))
    subprocess.run(["python3", "eas_alert.py"])
    forward_alert()
    send_notifications("An emergency alert has been triggered.")
    log_event(f"{current_user.id} triggered an alert")
    flash("Alert triggered successfully", "success")
    return redirect(url_for("index"))


@app.route("/log")
@login_required
def view_log():
    """
    Displays system logs.
    """
    logs = query_db("SELECT * FROM logs ORDER BY timestamp DESC")
    return render_template("alert_log.html", logs=logs)


@app.route("/manage_users", methods=["GET", "POST"])
@login_required
def manage_users():
    """
    Handles user management for admins.
    """
    if current_user.role != "admin":
        flash("You do not have permission to perform this action", "danger")
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]
        modify_db(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            [username, password, role],
        )
        flash("User added successfully", "success")
    users = query_db("SELECT username, role FROM users")
    return render_template("manage_users.html", users=users)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """
    Manages application settings.
    """
    if current_user.role != "admin":
        flash("You do not have permission to perform this action", "danger")
        return redirect(url_for("index"))
    if request.method == "POST":
        theme = request.form["theme"]
        language = request.form["language"]
        modify_db(
            "UPDATE settings SET theme = ?, language = ? WHERE id = 1",
            [theme, language],
        )
        flash("Settings updated successfully", "success")
    settings = query_db("SELECT theme, language FROM settings WHERE id = 1", one=True)
    return render_template("settings.html", settings=settings)


def log_event(event):
    """
    Logs an event in the database.
    """
    modify_db(
        "INSERT INTO logs (event, timestamp) VALUES (?, ?)",
        [event, datetime.now()],
    )


if __name__ == "__main__":
    # Failsafe for missing secrets in production
    if ENVIRONMENT == "production" and not FLASK_SECRET_KEY:
        raise RuntimeError(
            "Critical FLASK_SECRET_KEY is missing in production. Aborting."
        )

    # Initialize database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            event TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            theme TEXT DEFAULT 'light',
            language TEXT DEFAULT 'en'
        )
    """
    )
    cursor.execute(
        "INSERT OR IGNORE INTO settings (id, theme, language) VALUES (1, 'light', 'en')"
    )
    conn.commit()
    conn.close()

    print(f"Running in {ENVIRONMENT} mode...")
    app.run(
        host="0.0.0.0",
        port=5000,
        ssl_context=("certs/server.crt", "certs/server.key"),
    )
etenv("FLASK_DEBUG", "false").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

app.secret_key = FLASK_SECRET_KEY

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


class User(UserMixin):
    pass


# Database functions
def query_db(query, args=(), one=False):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv


def modify_db(query, args=()):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    conn.close()


@login_manager.user_loader
def user_loader(username):
    user_record = query_db(
        "SELECT username, role FROM users WHERE username = ?",
        [username],
        one=True,
    )
    if user_record is None:
        return None
    user = User()
    user.id = user_record[0]
    user.role = user_record[1]
    return user


@app.before_request
def enforce_https():
    """
    Enforce HTTPS in production environment.
    """
    if ENVIRONMENT == "production" and not request.is_secure:
        return jsonify({"error": "HTTPS is required in production"}), 403


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_record = query_db(
            "SELECT username, password, role FROM users WHERE username = ?",
            [username],
            one=True,
        )
        if user_record and user_record[1] == password:
            user = User()
            user.id = user_record[0]
            user.role = user_record[2]
            login_user(user)
            return redirect(url_for("index"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    alerts_count = query_db("SELECT COUNT(*) FROM logs", one=True)[0]
    user_count = query_db("SELECT COUNT(*) FROM users", one=True)[0]
    system_uptime = (
        datetime.now()
        - datetime.fromtimestamp(
            query_db("SELECT MIN(timestamp) FROM logs", one=True)[0]
        )
    ).total_seconds()
    return render_template(
        "index.html",
        role=current_user.role,
        alerts_count=alerts_count,
        user_count=user_count,
        system_uptime=system_uptime,
    )


@app.route("/trigger", methods=["POST"])
@login_required
def trigger_alert():
    if current_user.role != "admin":
        flash("You do not have permission to perform this action", "danger")
        return redirect(url_for("index"))
    subprocess.run(["python3", "eas_alert.py"])
    forward_alert()
    send_notifications("An emergency alert has been triggered.")
    log_event(f"{current_user.id} triggered an alert")
    flash("Alert triggered successfully", "success")
    return redirect(url_for("index"))


@app.route("/log")
@login_required
def view_log():
    logs = query_db("SELECT * FROM logs ORDER BY timestamp DESC")
    return render_template("alert_log.html", logs=logs)


@app.route("/manage_users", methods=["GET", "POST"])
@login_required
def manage_users():
    if current_user.role != "admin":
        flash("You do not have permission to perform this action", "danger")
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        modify_db(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            [username, password, role],
        )
        flash("User added successfully", "success")
    users = query_db("SELECT username, role FROM users")
    return render_template("manage_users.html", users=users)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if current_user.role != "admin":
        flash("You do not have permission to perform this action", "danger")
        return redirect(url_for("index"))
    if request.method == "POST":
        theme = request.form["theme"]
        language = request.form["language"]
        modify_db(
            "UPDATE settings SET theme = ?, language = ? WHERE id = 1",
            [theme, language],
        )
        flash("Settings updated successfully", "success")
    settings = query_db("SELECT theme, language FROM settings WHERE id = 1", one=True)
    return render_template("settings.html", settings=settings)


def log_event(event):
    modify_db(
        "INSERT INTO logs (event, timestamp) VALUES (?, ?)",
        [event, datetime.now()],
    )


if __name__ == "__main__":
    # Failsafe for missing secrets in production
    if ENVIRONMENT == "production" and not FLASK_SECRET_KEY:
        raise RuntimeError(
            "Critical FLASK_SECRET_KEY is missing in production. Aborting."
        )

    # Initialize database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            event TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            theme TEXT DEFAULT 'light',
            language TEXT DEFAULT 'en'
        )
    """
    )
    cursor.execute(
        "INSERT OR IGNORE INTO settings (id, theme, language) VALUES (1, 'light', 'en')"
    )
    conn.commit()
    conn.close()

    print(f"Running in {ENVIRONMENT} mode...")
    app.run(
        host="0.0.0.0",
        port=5000,
        ssl_context=("certs/server.crt", "certs/server.key"),
    )
