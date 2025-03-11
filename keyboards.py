# keyboards.py
from telebot import types

def create_main_menu():
    """Створює головне меню з кнопками."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("💱 Конвертувати"), types.KeyboardButton("📈 Курси валют"))
    markup.add(types.KeyboardButton("ℹ️ Допомога"), types.KeyboardButton("📜 Історія"))
    markup.add(types.KeyboardButton("🏦 Змінити банк"))  # Додаємо кнопку зміни банку
    return markup

def create_currency_keyboard(back_button=False):
    """Створює клавіатуру для вибору валют.

    Args:
        back_button: Чи додати кнопку "Назад".
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_usd = types.KeyboardButton("USD")
    btn_eur = types.KeyboardButton("EUR")
    btn_uah = types.KeyboardButton("UAH")
    btn_gbp = types.KeyboardButton("GBP")
    btn_pln = types.KeyboardButton("PLN")
    markup.add(btn_usd, btn_eur, btn_uah, btn_gbp, btn_pln)
    if back_button:
        markup.add(types.KeyboardButton("⬅️ Назад"))
    return markup

def create_swap_keyboard():
    """Створює inline-клавіатуру з кнопкою 'Поміняти місцями'."""
    markup = types.InlineKeyboardMarkup()
    swap_button = types.InlineKeyboardButton("🔄 Поміняти місцями", callback_data="swap_currencies")
    markup.add(swap_button)
    return markup

def create_source_keyboard():
    """Створює клавіатуру для вибору джерела курсів (банків)."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Monobank"), types.KeyboardButton("PrivatBank"))
    markup.add(types.KeyboardButton("⬅️ Назад"))
    return markup