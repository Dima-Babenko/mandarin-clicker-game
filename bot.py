from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Ініціалізація бази даних
def init_db():
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            user_id INTEGER PRIMARY KEY,
            points INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# Оновлення очків
@app.route("/update_score", methods=["POST"])
def update_score():
    data = request.json
    user_id = data.get("user_id")
    points = data.get("points", 0)

    if user_id is None:
        return jsonify({"error": "user_id is required"}), 400

    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()

    # Перевіряємо чи є користувач, і якщо ні, додаємо його
    cursor.execute("SELECT points FROM scores WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result is None:
        cursor.execute("INSERT INTO scores (user_id, points) VALUES (?, ?)", (user_id, points))
    else:
        current_points = result[0]
        new_points = current_points + points
        cursor.execute("UPDATE scores SET points = ? WHERE user_id = ?", (new_points, user_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Score updated successfully"}), 200

# Отримання очків
@app.route("/get_score", methods=["POST"])
def get_score():
    data = request.json
    user_id = data.get("user_id")

    if user_id is None:
        return jsonify({"error": "user_id is required"}), 400

    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()

    cursor.execute("SELECT points FROM scores WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return jsonify({"points": 0}), 200  # Якщо користувач не знайдений, повертаємо 0
    else:
        return jsonify({"points": result[0]}), 200

# Запуск сервера
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)