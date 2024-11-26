import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# Підключення до бази даних
conn = sqlite3.connect("scores.db", check_same_thread=False)
cursor = conn.cursor()

# Створюємо таблицю для збереження очок
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    score INTEGER DEFAULT 0
)
""")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробка команди /start."""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    # Перевіряємо, чи є користувач у базі
    cursor.execute("SELECT score FROM players WHERE player_id = ?", (user_id,))
    result = cursor.fetchone()

    if result is None:
        # Якщо гравця немає в базі, додаємо
        cursor.execute("INSERT INTO players (player_id, score) VALUES (?, ?)", (user_id, 0))
        conn.commit()
        current_score = 0
    else:
        current_score = result[0]

    # Привітання з поточним рахунком
    await update.message.reply_text(f"Привіт, {user_name}! У тебе {current_score} очків. Продовжуй грати!")

    # Кнопка для запуску гри
    keyboard = [
        [InlineKeyboardButton("Розпочати гру", web_app=WebAppInfo(url=f"https://dima-babenko.github.io/mandarin-clicker-game/?id={user_id}"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Натисни 'Розпочати гру', щоб перейти до гри!", reply_markup=reply_markup)

async def save_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Збереження очок від гри."""
    # API-запит з даними від гри
    user_id = int(update.message.text.split()[1])
    new_score = int(update.message.text.split()[2])

    # Оновлюємо очки в базі даних
    cursor.execute("UPDATE players SET score = ? WHERE player_id = ?", (new_score, user_id))
    conn.commit()
    await update.message.reply_text(f"Очки гравця {user_id} збережено: {new_score}")

def main():
    """Запуск бота."""
    TOKEN = "7699969593:AAEUzA5h4p69xj572NKUfYo4sgX-scWRwhk"
    application = Application.builder().token(TOKEN).build()

    # Додаємо обробники команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("save_score", save_score))

    # Запускаємо бота
    application.run_polling()

if __name__ == "__main__":
    main()