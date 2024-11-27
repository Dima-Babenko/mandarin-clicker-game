from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import sqlite3
import threading

# Ініціалізація Flask і Telegram
app = Flask(__name__)
TOKEN = "7699969593:AAEUzA5h4p69xj572NKUfYo4sgX-scWRwhk"

# Підключення до бази даних
def init_db():
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY,
            score INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# Функція для отримання очків
def get_user_score(user_id):
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM players WHERE player_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

# Функція для оновлення очків
def update_user_score(user_id, points_to_add):
    conn = sqlite3.connect("scores.db")
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM players WHERE player_id = ?", (user_id,))
    result = cursor.fetchone()

    if result is None:
        cursor.execute("INSERT INTO players (player_id, score) VALUES (?, ?)", (user_id, points_to_add))
    else:
        current_score = result[0]
        cursor.execute("UPDATE players SET score = ? WHERE player_id = ?", (current_score + points_to_add, user_id))

    conn.commit()
    conn.close()

# Telegram-обробник команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.first_name or "Гравець"

    # Отримуємо поточний рахунок
    score = get_user_score(user_id)

    # Створюємо кнопку для відкриття гри
    keyboard = [
        [InlineKeyboardButton("Розпочати гру", web_app=WebAppInfo(url=f"https://dima-babenko.github.io/mandarin-clicker-game/?id={user_id}"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Відправляємо повідомлення з кнопкою
    await update.message.reply_text(
        f"Привіт, {username}! У тебе {score} очків. Натисни на кнопку, щоб продовжити гру.",
        reply_markup=reply_markup
    )

# Flask-ендпоїнт для оновлення очків
@app.route("/update_score", methods=["POST"])
def update_score():
    data = request.json
    user_id = int(data["user_id"])
    points_to_add = int(data["points"])
    update_user_score(user_id, points_to_add)
    return jsonify({"status": "success"})

# Flask-ендпоїнт для отримання очків
@app.route("/get_score", methods=["GET"])
def get_score():
    user_id = int(request.args.get("user_id"))
    score = get_user_score(user_id)
    return jsonify({"score": score})

# Запуск Telegram-бота
def run_bot():
    application = Application.builder().token(TOKEN).build()

    # Додаємо обробники команд
    application.add_handler(CommandHandler("start", start))

    # Запуск бота
    application.run_polling()

# Запуск Flask-сервера
def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    init_db()
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    run_bot()