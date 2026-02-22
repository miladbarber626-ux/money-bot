import os
import sqlite3
import matplotlib.pyplot as plt

from keyboards import main_menu
from telegram import ReplyKeyboardMarkup

# کیبورد اصلی
main_menu = ReplyKeyboardMarkup([
    ['ثبت تراکنش', 'نمایش تراکنش‌ها'],
    ['نمودار', 'تنظیم هدف'],
], resize_keyboard=True)

async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # ارسال پیام خوش آمدگویی با دکمه‌ها
    await update.message.reply_text(
        "سلام! بگو چه کمکی از دستم بر میاد؟",
        reply_markup=main_menu  # این همون دکمه‌ها است که اضافه کردیم
    )
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")

conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT,
    category TEXT,
    amount INTEGER,
    date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS goals (
    user_id INTEGER PRIMARY KEY,
    amount INTEGER
)
""")

conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات حسابدار فعال شد ✅\nمثال:\nغذا 1300\n+حقوق 5000000\nهدف 20000000")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    today = datetime.now().strftime("%Y-%m-%d")

    if text.startswith("+"):
        parts = text[1:].split()
        if len(parts) == 2:
            category, amount = parts
            cursor.execute("INSERT INTO transactions (user_id, type, category, amount, date) VALUES (?, 'income', ?, ?, ?)",
                           (user_id, category, int(amount), today))
            conn.commit()
            await update.message.reply_text("درآمد ثبت شد ✅")

    elif text.startswith("هدف"):
        amount = int(text.split()[1])
        cursor.execute("REPLACE INTO goals (user_id, amount) VALUES (?, ?)", (user_id, amount))
        conn.commit()
        await update.message.reply_text("هدف ذخیره شد 🎯")

    elif text == "چقدر مونده":
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id=? AND type='income'", (user_id,))
        income = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id=? AND type='expense'", (user_id,))
        expense = cursor.fetchone()[0] or 0
        cursor.execute("SELECT amount FROM goals WHERE user_id=?", (user_id,))
        goal = cursor.fetchone()
        if goal:
            remaining = goal[0] - (income - expense)
            await update.message.reply_text(f"باقی‌مانده تا هدف: {remaining}")
        else:
            await update.message.reply_text("اول هدف تعیین کن.")

    elif text == "نمودار":
        cursor.execute("SELECT date, SUM(amount) FROM transactions WHERE user_id=? GROUP BY date", (user_id,))
        data = cursor.fetchall()
        if data:
            dates = [d[0] for d in data]
            amounts = [d[1] for d in data]
            plt.plot(dates, amounts)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig("chart.png")
            plt.close()
            await update.message.reply_photo(photo=open("chart.png", "rb"))
        else:
            await update.message.reply_text("داده‌ای برای نمودار نیست.")

    else:
        parts = text.split()
        if len(parts) == 2:
            category, amount = parts
            cursor.execute("INSERT INTO transactions (user_id, type, category, amount, date) VALUES (?, 'expense', ?, ?, ?)",
                           (user_id, category, int(amount), today))
            conn.commit()
            await update.message.reply_text("هزینه ثبت شد ✅")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
