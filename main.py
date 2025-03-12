import telebot
import logging
import os
from dotenv import load_dotenv
from telebot import types

# from api import get_monobank_rates, get_privatbank_rates  # Більше не потрібно напряму
from api import get_rates #Імпортуємо загальну функцію
from db import add_conversion, get_history
from utils import get_currency_name
from keyboards import create_main_menu, create_currency_keyboard, create_swap_keyboard, create_source_keyboard

# Завантажуємо .env, якщо використовується (якщо config.py, цей рядок не потрібен)
load_dotenv()

# Отримуємо токен (змінна оточення або з config.py)
TOKEN = os.getenv("TOKEN")  # Якщо використовуєш .env
# TOKEN = config.TOKEN # Якщо використовуєш config.py.  Розкоментуй, якщо config.py

if TOKEN is None:
    raise ValueError(".env файл не знайдено, або не вказано TOKEN, або немає змінної TOKEN у config.py")

bot = telebot.TeleBot(TOKEN)

# Налаштовуємо логування
logging.basicConfig(level=logging.INFO)

user_data = {}  # Словник для тимчасового зберігання даних користувача
DEFAULT_SOURCE = "monobank" #Банк за замовчуванням
# Обробник команди /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    show_main_menu(message)

# Обробник натискання на кнопки головного меню (і команда /start)
@bot.message_handler(func=lambda message: message.text in ["💱 Конвертувати", "📈 Курси валют", "ℹ️ Допомога", "📜 Історія", "🏦 Змінити банк", "Старт"])
def handle_main_menu(message):
    if message.text == "💱 Конвертувати" or message.text == "/convert":
        start_convert(message)
    elif message.text == "📈 Курси валют" or message.text == "/rates":
        show_rates(message)
    elif message.text == "ℹ️ Допомога" or message.text == "/help":
        send_help(message)
    elif message.text == "📜 Історія" or message.text == "/history":
        show_history(message)
    elif message.text == "🏦 Змінити банк":
        select_source(message)
    elif message.text == "Старт":  # Додаткова обробка кнопки "Старт"
        send_welcome(message)


def show_main_menu(message):
    markup = create_main_menu()  # Використовуємо функцію з keyboards.py
    user_name = message.from_user.first_name  # Отримуємо ім'я користувача
    chat_id = message.chat.id  # Отримуємо chat_id
    source = user_data.get(chat_id, {}).get('source', DEFAULT_SOURCE)  # Отримуємо джерело
    source_name = "Monobank" if source == "monobank" else "ПриватБанк"  # Назва для повідомлення
    bot.reply_to(message, f"👋 Привіт, {user_name}! Я бот-конвертер валют!\n\n"
                          f"Я допоможу тобі швидко конвертувати валюти за курсом {source_name}. 🏦\n\n"  # Повідомлення з назвою банку
                          "Вибери дію:", reply_markup=markup)   # Показуємо головне меню

# Обробник команди /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
Я можу допомогти тобі конвертувати валюти за курсом Monobank або ПриватБанку.

Доступні команди:
/start - Почати роботу з ботом (показує головне меню).
/help - Показати це повідомлення.
/convert - Конвертувати валюту.
/rates - Показати курси валют.
/history - Показати історію конвертацій.
/source - Змінити джерело курсів валют (Monobank/Privatbank).

Ви також можете використовувати мене в inline-режимі. Введіть в будь-якому чаті:
`@Converter_tutorial1_bot <сума> <валюта> to <валюта>`
Наприклад: `@Converter_tutorial1_bot 100 USD to UAH`
    """
    bot.reply_to(message, help_text, parse_mode="Markdown")  # parse_mode для Markdown
# Обробник команди /rates (показує курси валют)
@bot.message_handler(commands=['rates'])
def show_rates(message):
    chat_id = message.chat.id
    source = user_data.get(chat_id, {}).get('source', DEFAULT_SOURCE) # Отримуємо джерело з user_data
    rates = get_rates(source)  # Використовуємо функцію get_rates з api.py
    if rates:
        if source == "monobank":
            response_text = f"*Курси валют {source}:*\n```\n"  # Markdown (жирний і моноширинний)
            response_text += "Валюта | Купівля | Продаж\n"
            response_text += "------- | -------- | --------\n"
            for rate in rates:
                currency_a = get_currency_name(rate.get('currencyCodeA'), source)  # utils.get_...
                currency_b = get_currency_name(rate.get('currencyCodeB'), source)
                rate_buy = rate.get('rateBuy')
                rate_sell = rate.get('rateSell')

                if rate_buy is not None and rate_sell is not None:
                    response_text += f"{currency_a}/{currency_b}    | {rate_buy:8.4f} | {rate_sell:8.4f}\n"
            response_text += "```"
            bot.reply_to(message, response_text, parse_mode="Markdown")  # Вказуємо parse_mode

        elif source == "privatbank":
            response_text = f"*Курси валют {source}:*\n```\n"
            response_text += "Валюта | Купівля | Продаж\n"
            response_text += "------- | -------- | --------\n"
            for rate in rates:
                currency_a = rate.get('ccy')  # Використовуємо 'ccy' для ПриватБанку
                currency_b = rate.get('base_ccy')
                rate_buy = rate.get('buy')
                rate_sell = rate.get('sale')
                if currency_a and currency_b and rate_buy and rate_sell:
                    response_text += f"{currency_a}/{currency_b}    | {float(rate_buy):8.4f} | {float(rate_sell):8.4f}\n"
            response_text += "```"
            bot.reply_to(message, response_text, parse_mode="Markdown")
        else:
            bot.reply_to(message, f"Невідоме джерело курсів: {source}")

    else:
        bot.reply_to(message, f"Не вдалося отримати курси валют з {source}.")
# Додаємо обробник команди /source та функцію select_source
@bot.message_handler(commands=['source'])
def select_source(message):
    markup = create_source_keyboard() # Клавіатура з вибором банків
    bot.reply_to(message, "Виберіть джерело курсів валют:", reply_markup=markup)
    bot.register_next_step_handler(message, process_source_selection)

def process_source_selection(message):
    chat_id = message.chat.id
    markup = create_source_keyboard()
    if message.text == "⬅️ Назад": #назад в головне меню
        show_main_menu(message)
        return
    if message.text not in ["Monobank", "PrivatBank"]:
        bot.reply_to(message, "Будь ласка, виберіть джерело зі списку.", reply_markup=markup)
        bot.register_next_step_handler(message, process_source_selection)
        return

    source = message.text.lower()  # Приводимо до нижнього регістра
    if source == "privatbank":
        source = "privatbank"  # Уніфікуємо назву

    # Зберігаємо вибір користувача в user_data
    if chat_id not in user_data:
      user_data[chat_id] = {} #Створюємо, якщо немає
    user_data[chat_id]['source'] = source
    bot.reply_to(message, f"Вибрано джерело курсів: {message.text}", reply_markup=types.ReplyKeyboardRemove())
    show_main_menu(message)  # Повертаємось в головне меню
# Обробник команди /convert (початок процесу конвертації)
@bot.message_handler(commands=['convert'])
def start_convert(message):
    chat_id = message.chat.id
    user_data[chat_id] = user_data.get(chat_id, {}) #Створюємо пустий словник, або беремо існуючий
    user_data[chat_id]['state'] = 'awaiting_choice'  # Початковий стан

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("USD/UAH"), types.KeyboardButton("EUR/UAH"))
    markup.add(types.KeyboardButton("Ввести вручну"))
    markup.add(types.KeyboardButton("⬅️ Назад"))  # Додаємо кнопку "Назад"

    msg = bot.reply_to(message, "Виберіть швидку конвертацію або введіть дані вручну:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_choice)  # Переходимо до вибору типу конвертації

# Обробник вибору типу конвертації (швидка/ручна)
def process_choice(message):
    chat_id = message.chat.id

    if message.text == "⬅️ Назад":
        show_main_menu(message)  # Повернення в головне меню
        return

    if message.text == "USD/UAH":
        user_data[chat_id]['from_currency'] = "USD"
        user_data[chat_id]['to_currency'] = "UAH"
        user_data[chat_id]['state'] = 'awaiting_amount'
        bot.reply_to(message, "Введіть суму в USD:", reply_markup=types.ReplyKeyboardRemove()) #Клавіатуру прибираємо
        bot.register_next_step_handler(message, process_amount) #Переходимо до process_amount

    elif message.text == "EUR/UAH":
        user_data[chat_id]['from_currency'] = "EUR"
        user_data[chat_id]['to_currency'] = "UAH"
        user_data[chat_id]['state'] = 'awaiting_amount'
        bot.reply_to(message, "Введіть суму в EUR:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, process_amount) #Переходимо до process_amount

    elif message.text == "Ввести вручну":
        user_data[chat_id]['state'] = 'awaiting_amount'
        bot.reply_to(message, "Введіть суму:", reply_markup=types.ReplyKeyboardRemove()) #Прибираємо клавіатуру
        bot.register_next_step_handler(message, process_amount) #Передаємо process_amount
    else:
        bot.reply_to(message, "Невірний вибір.")
        start_convert(message)  # Починаємо спочатку
# Обробник введення суми (об'єднаний для швидкої та ручної конвертації)
def process_amount(message):
    """
    Обробляє введення суми для конвертації.  Працює як для швидкої конвертації,
    так і для ручного введення валют.  Перевіряє коректність введених даних.
    """
    chat_id = message.chat.id
    markup = create_currency_keyboard(back_button=True)  # Створюємо клавіатуру вибору валют з кнопкою "Назад"

    if message.text == "⬅️ Назад":
        start_convert(message)  # Повертаємось до початку (вибір швидкої/ручної конвертації)
        return

    # Перевірка стану.  Якщо стан не 'awaiting_amount', то щось пішло не так.
    # (наприклад, користувач ввів команду /start під час конвертації).
    if chat_id not in user_data or user_data[chat_id].get('state') != 'awaiting_amount':
        bot.reply_to(message, "Сталася помилка. Почніть конвертацію знову.", reply_markup=types.ReplyKeyboardRemove())
        if chat_id in user_data:  # Видаляємо дані, якщо вони є, щоб не було конфліктів
            del user_data[chat_id]
        show_main_menu(message)  # Повертаємо в головне меню
        return  # Виходимо з функції

    try:
        # Намагаємося перетворити введене значення на число (float)
        amount = float(message.text)
        if amount <= 0:
            # Якщо сума менша або дорівнює нулю, генеруємо виняток
            raise ValueError("Сума повинна бути більшою за нуль")

        # Якщо все добре (сума - коректне число), зберігаємо її в user_data
        user_data[chat_id]['amount'] = amount
        user_data[chat_id]['state'] = 'awaiting_from_currency'  # Змінюємо стан на "очікування вихідної валюти"

        # Якщо це швидка конвертація (валюти вже визначені), одразу переходимо до конвертації
        if 'from_currency' in user_data[chat_id] and 'to_currency' in user_data[chat_id]:
             user_data[chat_id]['state'] = None  # Скидаємо стан
             convert_currency(chat_id, message)
             return
        # Якщо ручне введення, переходимо до вибору валюти
        msg = bot.reply_to(message, "Виберіть вихідну валюту:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_from_currency_step)


    except ValueError as e:
        # Якщо виникла помилка (некоректне число), повідомляємо про це користувача
        bot.reply_to(message, f"Будь ласка, введіть додатнє числове значення. Помилка: {e}", reply_markup=types.ReplyKeyboardRemove())
        # Повторно запитуємо суму
        msg = bot.reply_to(message, "Введіть суму:")
        bot.register_next_step_handler(msg, process_amount)
# Обробник вибору вихідної валюти
def process_from_currency_step(message):
    chat_id = message.chat.id
    markup = create_currency_keyboard(back_button=True)  # Клавіатура з кнопкою "Назад"
    if message.text == "⬅️ Назад":
        # Повертаємось до введення суми.  Змінюємо стан.
        user_data[chat_id]['state'] = 'awaiting_amount'
        msg = bot.reply_to(message, "Введіть суму:", reply_markup=types.ReplyKeyboardRemove()) #Прибираємо стару клавіатуру
        bot.register_next_step_handler(msg, process_amount)
        return

    from_currency = message.text  # Отримуємо текст повідомлення (назву валюти)

    # Перевіряємо, чи є вибрана валюта в списку дозволених
    if from_currency not in ["USD", "EUR", "UAH", "GBP", "PLN"]:
        bot.reply_to(message, "Невірна валюта.", reply_markup=markup)
        msg = bot.reply_to(message, "Виберіть вихідну валюту:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_from_currency_step)  # Знову викликаємо цю ж функцію
        return

    # Якщо валюта коректна, зберігаємо її в user_data
    user_data[chat_id]['from_currency'] = from_currency
    user_data[chat_id]['state'] = 'awaiting_to_currency'  # Змінюємо стан на "очікування цільової валюти"
    msg = bot.reply_to(message, "Виберіть цільову валюту:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_to_currency_step)  # Переходимо до вибору цільової валюти

# Обробник вибору цільової валюти
def process_to_currency_step(message):
    chat_id = message.chat.id
    markup = create_currency_keyboard(back_button=True)  # Клавіатура з кнопкою "Назад"

    if message.text == "⬅️ Назад":
        # Повертаємось до вибору *вихідної* валюти, змінюємо стан
        user_data[chat_id]['state'] = 'awaiting_from_currency'
        msg = bot.reply_to(message, "Виберіть вихідну валюту:", reply_markup=markup) #Показуємо стару клавіатуру
        bot.register_next_step_handler(msg, process_from_currency_step)
        return

    to_currency = message.text  # Отримуємо текст повідомлення (назву цільової валюти)

    # Перевірка, чи валюта є в списку дозволених
    if to_currency not in ["USD", "EUR", "UAH", "GBP", "PLN"]:
        bot.reply_to(message, "Невірна валюта.", reply_markup=markup)
        msg = bot.reply_to(message, "Виберіть цільову валюту:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_to_currency_step)  # Знову викликаємо цю ж функцію
        return

    # Якщо все добре, зберігаємо цільову валюту в user_data
    user_data[chat_id]['to_currency'] = to_currency
    user_data[chat_id]['state'] = None  # Скидаємо стан (конвертація завершена/готова до конвертації)

    # Додаємо кнопку "Поміняти місцями"
    markup = create_swap_keyboard()  # Використовуємо функцію з keyboards.py
    convert_currency(chat_id, message, markup)  # Переходимо до функції конвертації
def convert_currency(chat_id, message, reply_markup=None):
    """
    Виконує конвертацію валюти на основі даних в user_data,
    і надсилає результат.
    """
    source = user_data.get(chat_id, {}).get('source', DEFAULT_SOURCE)
    rates = get_rates(source)

    if not rates:
        bot.reply_to(message, "Не вдалося отримати курси валют.", reply_markup=types.ReplyKeyboardRemove())
        if chat_id in user_data:
            del user_data[chat_id]
        show_main_menu(message)
        return

    rate = None
    for r in rates:
        if source == "monobank":
            if get_currency_name(r.get('currencyCodeA')) == user_data[chat_id]['from_currency'] and \
                get_currency_name(r.get('currencyCodeB')) == user_data[chat_id]['to_currency']:
                rate = r
                break
            if get_currency_name(r.get('currencyCodeB')) == user_data[chat_id]['from_currency'] and \
                get_currency_name(r.get('currencyCodeA')) == user_data[chat_id]['to_currency']:
                rate = r
                break
        elif source == "privatbank":
            if r.get('ccy') == user_data[chat_id]['from_currency'] and r.get('base_ccy') == user_data[chat_id]['to_currency']:
                rate = r
                break

    if not rate:
        bot.reply_to(message, "Не вдалося знайти курс для цієї пари валют.", reply_markup=types.ReplyKeyboardRemove())
        if chat_id in user_data:
            del user_data[chat_id]
        show_main_menu(message)
        return

    if source == "monobank":
        if 'rateBuy' in rate and 'rateSell' in rate:
            if user_data[chat_id]['from_currency'] == 'UAH':
                converted_amount = user_data[chat_id]['amount'] / rate['rateSell']
            elif user_data[chat_id]['to_currency'] == 'UAH':
                    converted_amount = user_data[chat_id]['amount'] * rate['rateBuy']
            else:  # Між іноземними
                if 'rateCross' in rate:
                        converted_amount = user_data[chat_id]['amount'] * rate['rateCross']
                else:
                    bot.reply_to(message, "Не вдалося знайти крос-курс.", reply_markup=types.ReplyKeyboardRemove())
                    if chat_id in user_data:
                        del user_data[chat_id]
                    show_main_menu(message)
                    return
        else:
            bot.reply_to(message, "Відсутні необхідні курси (купівлі/продажу).", reply_markup=types.ReplyKeyboardRemove())
            if chat_id in user_data:
                del user_data[chat_id]
            show_main_menu(message)
            return

    elif source == "privatbank":
        if 'buy' in rate and 'sale' in rate:
            if user_data[chat_id]['from_currency'] == "UAH":
                converted_amount = user_data[chat_id]['amount'] / float(rate['sale'])  # Не забуваємо про float
            else:
                converted_amount = user_data[chat_id]['amount'] * float(rate['buy']) # Не забуваємо про float
        else:
                bot.reply_to(message, "Відсутні необхідні курси (купівлі/продажу).", reply_markup=types.ReplyKeyboardRemove())
                if chat_id in user_data:
                    del user_data[chat_id]
                show_main_menu(message)
                return


    formatted_amount = "{:.2f}".format(converted_amount)
    bot.reply_to(message, f"Результат: {formatted_amount} {user_data[chat_id]['to_currency']}", reply_markup=reply_markup)

    add_conversion(chat_id, user_data[chat_id]['amount'], user_data[chat_id]['from_currency'],
                    user_data[chat_id]['to_currency'], converted_amount)
    if chat_id in user_data:
        del user_data[chat_id]
# Обробник натискання на кнопку "Поміняти місцями"
@bot.callback_query_handler(func=lambda call: call.data == "swap_currencies")
def handle_swap_currencies(call):
    chat_id = call.message.chat.id
    if chat_id in user_data:
        # Міняємо місцями from_currency і to_currency
        user_data[chat_id]['from_currency'], user_data[chat_id]['to_currency'] = \
            user_data[chat_id]['to_currency'], user_data[chat_id]['from_currency']

        # Повторно викликаємо функцію convert_currency, передаючи *НОВУ* клавіатуру
        markup = create_swap_keyboard()  # Створюємо нову клавіатуру
        convert_currency(chat_id, call.message, markup)  # Викликаємо функцію конвертації
        bot.answer_callback_query(call.id)  # Закриваємо callback

    else:
        bot.answer_callback_query(call.id, "Дані про конвертацію застаріли. Почніть спочатку.")
        show_main_menu(call.message)


# Обробник команди /history (показує історію конвертацій)
@bot.message_handler(commands=['history'])
def show_history(message):
    chat_id = message.chat.id
    history = get_history(chat_id)  # Використовуємо функцію з db.py
    if history:
        response_text = "*Історія конвертацій:*\n```\n"  # Markdown (жирний і моноширинний шрифт)
        response_text += "Сума | Звідки | Куди | Результат | Час\n"
        response_text += "------|-------|------|-----------|-----\n"
        for row in history:
            amount, from_currency, to_currency, converted_amount, timestamp = row
            response_text += f"{amount:5.2f} | {from_currency:5} | {to_currency:4} | {converted_amount:9.2f} | {timestamp}\n"
        response_text += "```"
        bot.reply_to(message, response_text, parse_mode="Markdown")  # parse_mode='Markdown'
    else:
        bot.reply_to(message, "Історія конвертацій порожня.")

# Обробник inline-запитів
@bot.inline_handler(lambda query: True)
def inline_converter(inline_query):
    """
    Обробляє inline-запити
    """
    try:
        parts = inline_query.query.split()
        if len(parts) >= 4 and parts[2].lower() == "to":
            amount = float(parts[0])
            from_currency = parts[1].upper()
            to_currency = parts[3].upper()

            if from_currency not in ["USD", "EUR", "UAH", "GBP", "PLN"] or to_currency not in ["USD", "EUR", "UAH", "GBP", "PLN"]:
                raise ValueError("Invalid currency")

            rates = get_rates("monobank")  # Тільки Monobank для inline
            if rates:
                rate = None
                for r in rates:
                    if get_currency_name(r.get('currencyCodeA')) == from_currency and \
                       get_currency_name(r.get('currencyCodeB')) == to_currency:
                        rate = r
                        break
                    if get_currency_name(r.get('currencyCodeB')) == from_currency and \
                       get_currency_name(r.get('currencyCodeA')) == to_currency:
                        rate = r
                        break

                if rate:
                    if rate.get('rateBuy') is not None and rate.get('rateSell') is not None:
                        if from_currency == 'UAH':
                            converted_amount = amount / rate.get('rateSell')
                        else:
                            converted_amount = amount * rate.get('rateBuy')
                    elif rate.get('rateCross') is not None:
                        converted_amount = amount * rate.get('rateCross')
                    else:
                        raise ValueError("Currency rate not found")

                    result = "{:.2f}".format(converted_amount)
                    rate_text = ""
                    if rate.get('rateBuy') and rate.get('rateSell'):
                       if from_currency == "UAH":
                         rate_text = f"Курс: 1 {to_currency} = {rate.get('rateSell'):.4f} {from_currency}"
                       else:
                          rate_text = f"Курс: 1 {from_currency} = {rate.get('rateBuy'):.4f} {to_currency}"
                    elif rate.get('rateCross'):
                       rate_text = f"Курс: 1 {from_currency} = {rate.get('rateCross'):.4f} {to_currency}"

                    r = types.InlineQueryResultArticle(
                        '1',
                        f'Convert {amount} {from_currency} to {to_currency}',
                        types.InputTextMessageContent(f"{amount} {from_currency} = {result} {to_currency}\n{rate_text}")
                    )
                    bot.answer_inline_query(inline_query.id, [r])

                else:
                  raise ValueError("Currency rate not found")
            else:
              raise ValueError("Could not retrieve currency rates")

        else:
            return

    except ValueError as e:
        print(f"Inline query error: {e}")
        return
    except Exception as e:
        print(f"Inline query error: {e}")
        return

# Запуск бота
logging.info("Бот запущено...")
bot.infinity_polling()