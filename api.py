import requests  # Для виконання HTTP-запитів до API
import json  # Для обробки JSON-відповідей від API
import os  # Для доступу до змінних оточення
import time  # Імпорт модуля time для роботи з часом (для кешування)
from dotenv import load_dotenv  # Для завантаження змінних оточення з .env

load_dotenv()  # Завантажуємо змінні оточення

# Отримуємо URL API Monobank з змінної оточення
MONOBANK_API_URL = os.getenv("MONOBANK_API_URL")
if MONOBANK_API_URL is None:
    raise ValueError("MONOBANK_API_URL is not set in .env file")

# URL API ПриватБанку (готівковий курс)
PRIVATBANK_API_URL = "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5"
# PRIVATBANK_API_URL = "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=11"  # Безготівковий (закоментовано)

# Словник для кешування курсів валют.  Ключі - назви банків, значення - словники з даними і часом.
cached_rates = {}
CACHE_LIFETIME = 900  # Час життя кешу в секундах (15 хвилин)
def get_monobank_rates(cached=True):
    """Отримує курси валют з API Monobank, використовуючи кеш."""
    now = time.time()  # Поточний час (в секундах з початку епохи)

    # Перевірка наявності даних в кеші та їх актуальності
    if cached and 'monobank' in cached_rates and (now - cached_rates['monobank'].get('timestamp', 0)) < CACHE_LIFETIME:
        print("Using cached data (Monobank)")  # Повідомлення для налагодження (можна вимкнути)
        return cached_rates['monobank']['data']  # Повертаємо дані з кешу

    # Якщо даних в кеші немає або вони застарілі, робимо запит до API
    try:
        response = requests.get(MONOBANK_API_URL)
        response.raise_for_status()  # Перевірка на HTTP-помилки (4xx, 5xx)
        data = response.json()  # Перетворюємо JSON-відповідь на словник Python
        if not data: # Перевірка, чи API повернув не пусті дані
            raise ValueError("API Monobank returned empty data.")
        cached_rates['monobank'] = {'data': data, 'timestamp': now}  # Зберігаємо дані в кеш
        return data  # Повертаємо дані

    # Обробка помилок
    except requests.exceptions.RequestException as e:
        print(f"Помилка запиту до API Monobank: {e}")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Помилка обробки даних від API Monobank: {e}")
    return None  # Повертаємо None у разі будь-якої помилки
def get_privatbank_rates(cached=True):
    """Отримує курси валют з API ПриватБанку, використовуючи кеш."""
    now = time.time()

    # Перевірка кешу
    if cached and 'privatbank' in cached_rates and (now - cached_rates['privatbank'].get('timestamp', 0)) < CACHE_LIFETIME:
        # print("Using cached data (PrivatBank)") # Можна закоментувати, щоб не виводити повідомлення
        return cached_rates['privatbank']['data']

    # Запит до API
    try:
        response = requests.get(PRIVATBANK_API_URL)
        response.raise_for_status()
        data = response.json()
        if not data: # Перевірка на пустий результат
            raise ValueError("API PrivatBank returned empty data.")

        cached_rates['privatbank'] = {'data': data, 'timestamp': now}  # Зберігаємо в кеш
        return data

    # Обробка помилок
    except requests.exceptions.RequestException as e:
        print(f"Помилка запиту до API ПриватБанку: {e}")
        return None
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Помилка обробки даних від API ПриватБанку: {e}")
        return None
def get_rates(source="monobank", cached=True):
    """
    Отримує курси валют з вказаного джерела (Monobank або PrivatBank).

    Args:
        source: Назва джерела ('monobank' або 'privatbank').  За замовчуванням 'monobank'.
        cached: Чи використовувати кешування (True/False). За замовчуванням True.

    Returns:
        Словник з курсами валют або None, якщо сталася помилка, або якщо вказано невірне джерело.
    """
    if source == "monobank":
        return get_monobank_rates(cached)  # Викликаємо функцію для Monobank
    elif source == "privatbank":
        return get_privatbank_rates(cached)  # Викликаємо функцію для PrivatBank
    else:
        return None  # Повертаємо None, якщо джерело не підтримується