from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    keyboard = [
        [InlineKeyboardButton("➕ ثبت درآمد", callback_data="add_income")],
        [InlineKeyboardButton("➖ ثبت هزینه", callback_data="add_expense")],
        [InlineKeyboardButton("📊 گزارش", callback_data="report")],
        [InlineKeyboardButton("🎯 هدف مالی", callback_data="goal")]
    ]
    return InlineKeyboardMarkup(keyboard)
