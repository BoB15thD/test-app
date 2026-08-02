import os
import re
import sqlite3
import subprocess

from flask import Flask, request, jsonify

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", "app.db")
LOG_DIR = os.path.realpath(os.environ.get("LOG_DIR", "/var/app/logs"))
ADMIN_TOOL = "/usr/local/bin/admin-tool"

ALLOWED_ADMIN_COMMANDS = frozenset({"status", "version", "reload", "flush-cache"})

HOSTNAME_RE = re.compile(
    r"\A(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\Z"
)


def get_connection():
    return sqlite3.connect(DB_PATH)


@app.route("/api/user")
def get_user():
    user_id = request.args.get("id", "")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email FROM users WHERE id = ?",
            (user_id,),
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    return jsonify([{"id": r[0], "username": r[1], "email": r[2]} for r in rows])


@app.route("/api/search")
def search_products():
    keyword = request.args.get("q", "")

    escaped = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    pattern = f"%{escaped}%"

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, price FROM products WHERE name LIKE ? ESCAPE '\\'",
            (pattern,),
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    return jsonify([{"name": r[0], "price": r[1]} for r in rows])


@app.route("/api/ping")
def ping_host():
    host = request.args.get("host", "localhost")

    if not HOSTNAME_RE.match(host):
        return jsonify({"error": "잘못된 호스트명입니다"}), 400

    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-w", "3", "--", host],
            shell=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        return jsonify({"error": "요청 시간이 초과되었습니다"}), 504

    return jsonify({"output": result.stdout, "error": result.stderr})


@app.route("/api/logs")
def read_log():
    filename = request.args.get("file", "app.log")

    if not filename or "/" in filename or "\\" in filename or filename.startswith("."):
        return jsonify({"error": "잘못된 파일명입니다"}), 400

    path = os.path.realpath(os.path.join(LOG_DIR, filename))
    if not path.startswith(LOG_DIR + os.sep):
        return jsonify({"error": "잘못된 경로입니다"}), 400

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except (FileNotFoundError, IsADirectoryError):
        return jsonify({"error": "파일을 찾을 수 없습니다"}), 404
    except PermissionError:
        return jsonify({"error": "접근 권한이 없습니다"}), 403

    return jsonify({"content": content})


@app.route("/api/admin/exec", methods=["POST"])
def admin_exec():
    command = request.form.get("cmd", "")

    if command not in ALLOWED_ADMIN_COMMANDS:
        return jsonify({"error": "허용되지 않은 명령입니다"}), 400

    try:
        result = subprocess.run(
            [ADMIN_TOOL, command],
            shell=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        return jsonify({"error": "명령 실행 시간이 초과되었습니다"}), 504

    return jsonify({"output": result.stdout, "error": result.stderr})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
