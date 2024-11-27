import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import json
from flask import Flask, request

# Налаштовуємо Flask для API
app = Flask(__name__)

# Налаштування бази даних
conn = sqlite3.connect("scores.db", check_same_thread=False)
cursor = conn.cursor()

# Створення таблиці для збереження очків гравців
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    score INTEGER DEFAULT 0
)
""")
conn.commit()

# Telegram-бот: команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показує кнопку для запуску гри."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    # Перевіряємо чи є гравець у базі
    cursor.execute("SELECT score FROM players WHERE player_id = ?", (user_id,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute("INSERT INTO players (player_id, score) VALUES (?, ?)", (user_id, 0))
        conn.commit()

    # Виводимо поточний рахунок
    await update.message.reply_text(f"Привіт, {user_name}! Очки збережено. Натисни кнопку, щоб грати!")

    # Кнопка запуску гри
    keyboard = [
        [InlineKeyboardButton("Розпочати гру", web_app=WebAppInfo(url=f"https://dima-babenko.github.io/mandarin-clicker-game/?id={user_id}"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Натисни кнопку, щоб почати гру!", reply_markup=reply_markup)

# API-метод для отримання очків
@app.route("/get_score", methods=["POST"])
def get_score():
    data = request.json
    user_id = data["user_id"]

    # Отримуємо очки з бази
    cursor.execute("SELECT score FROM players WHERE player_id = ?", (user_id,))
    result = cursor.fetchone()

    if result is None:
        return json.dumps({"status": "error", "message": "Player not found"}), 404
    return json.dumps({"status": "success", "score": result[0]}), 200

# API-метод для оновлення очків
@app.route("/update_score", methods=["POST"])
def update_score():
    data = request.json
    user_id = data["user_id"]
    points = data["points"]

    cursor.execute("UPDATE players SET score = score + ? WHERE player_id = ?", (points, user_id))
    conn.commit()
    return json.dumps({"status": "success"}), 200

def main():
    """Запуск Telegram-бота."""
    TOKEN = "7699969593:AAEUzA5h4p69xj572NKUfYo4sgX-scWRwhk"
    application = Application.builder().token(TOKEN).build()

    # Додаємо обробники
    application.add_handler(CommandHandler("start", start))

    # Запускаємо Flask API та Telegram-бот
    from threading import Thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()
    application.run_polling()

if __name__ == "__main__":
    main()