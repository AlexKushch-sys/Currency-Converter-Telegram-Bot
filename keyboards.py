from telebot import types

def create_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_convert = types.KeyboardButton("💱 Конвертувати")  # Змінено емодзі
    btn_rates = types.KeyboardButton("📈 Курси валют")
    btn_help = types.KeyboardButton("ℹ️ Допомога")
    btn_history = types.KeyboardButton("📜 Історія")
    btn_source = types.KeyboardButton("🏦 Змінити банк")  # Додано кнопку зміни банку
    markup.row(btn_convert, btn_rates)
    markup.row(btn_help, btn_history)
    markup.row(btn_source) # Додаємо кнопку в меню
    return markup

def create_currency_keyboard(back_button=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("USD", "EUR", "UAH")
    markup.row("GBP", "PLN")
    if back_button:
        markup.row("⬅️ Назад")  # Додаємо кнопку "Назад"
    return markup

def create_swap_keyboard():
    markup = types.InlineKeyboardMarkup()  # Inline-клавіатура
    swap_button = types.InlineKeyboardButton("🔄 Поміняти місцями", callback_data="swap_currencies")
    markup.add(swap_button)
    return markup

# Додаємо функцію створення клавіатури вибору джерела
def create_source_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_monobank = types.KeyboardButton("Monobank")
    btn_privatbank = types.KeyboardButton("PrivatBank")
    btn_back = types.KeyboardButton("⬅️ Назад")  # Кнопка "Назад"
    markup.row(btn_monobank, btn_privatbank)
    markup.row(btn_back)
    return markup