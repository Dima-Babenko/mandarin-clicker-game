import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# Налаштування бази даних
conn = sqlite3.connect("scores.db", check_same_thread=False)
cursor = conn.cursor()

# Створення таблиці для збереження даних гравців
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    score INTEGER DEFAULT 0
)
""")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробляє команду /start, надсилає очки гравця та кнопку для запуску гри."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    # Отримуємо очки гравця з бази
    cursor.execute("SELECT score FROM players WHERE player_id = ?", (user_id,))
    result = cursor.fetchone()

    if result is None:
        # Якщо гравця немає, додаємо його до бази
        cursor.execute("INSERT INTO players (player_id, score) VALUES (?, ?)", (user_id, 0))
        conn.commit()
        current_score = 0
    else:
        current_score = result[0]

    # Відповідь із поточним рахунком
    await update.message.reply_text(f"Привіт, {user_name}! У тебе {current_score} очків.")

    # Кнопка для гри
    keyboard = [
        [InlineKeyboardButton("Розпочати гру", web_app=WebAppInfo(url=f"https://dima-babenko.github.io/mandarin-clicker-game/?id={user_id}"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Натисни 'Розпочати гру', щоб грати!", reply_markup=reply_markup)

async def save_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Оновлює очки гравця в базі."""
    # Отримуємо текст, який містить `user_id` та новий `score`
    data = update.message.text.split()
    user_id = int(data[1])
    new_score = int(data[2])

    # Оновлюємо очки гравця
    cursor.execute("UPDATE players SET score = ? WHERE player_id = ?", (new_score, user_id))
    conn.commit()
    await update.message.reply_text(f"Очки гравця {user_id} оновлено: {new_score}")

def main():
    """Запуск Telegram-бота."""
    TOKEN = "Ваш_токен_бота"
    application = Application.builder().token(TOKEN).build()

    # Обробники команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("save_score", save_score))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()