# api.py
import requests
import json
import os
import time  # Імпорт time
from dotenv import load_dotenv

load_dotenv()
MONOBANK_API_URL = os.getenv("MONOBANK_API_URL")
if MONOBANK_API_URL is None:
    raise ValueError("MONOBANK_API_URL is not set in .env file")

PRIVATBANK_API_URL = "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5"  # Готівковий курс
# PRIVATBANK_API_URL = "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=11"  # Безготівковий курс (якщо треба)

cached_rates = {}  # Кеш для всіх банків: {'monobank': {'data': ..., 'timestamp': ...}, 'privatbank': ...}
CACHE_LIFETIME = 900  # 15 хвилин


def get_monobank_rates(cached=True):
    """Отримує курси валют з API Monobank, використовуючи кеш."""
    now = time.time()

    if cached and 'monobank' in cached_rates and (now - cached_rates['monobank'].get('timestamp', 0)) < CACHE_LIFETIME:
        print("Using cached data (Monobank)")  # Для налагодження
        return cached_rates['monobank']['data']

    try:
        response = requests.get(MONOBANK_API_URL)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise ValueError("API Monobank returned empty data.")

        cached_rates['monobank'] = {'data': data, 'timestamp': now}  # Зберігаємо в кеш
        return data

    except requests.exceptions.RequestException as e:
        print(f"Помилка запиту до API Monobank: {e}")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Помилка обробки даних від API Monobank: {e}")
    return None  # Повертаємо None у разі помилки

def get_privatbank_rates(cached=True):
    """Отримує курси валют з API ПриватБанку."""
    now = time.time()

    if cached and 'privatbank' in cached_rates and (now - cached_rates['privatbank'].get('timestamp', 0)) < CACHE_LIFETIME:
        # print("Using cached data (PrivatBank)") #Для налагодження
        return cached_rates['privatbank']['data']
    try:
        response = requests.get(PRIVATBANK_API_URL)
        response.raise_for_status()
        data = response.json()  # Приват повертає JSON
        if not data: #перевірка на пустий результат
            raise ValueError("API PrivatBank returned empty data.")

        cached_rates['privatbank'] = {'data': data, 'timestamp': now}  # Зберігаємо в кеш
        return data

    except requests.exceptions.RequestException as e:
        print(f"Помилка запиту до API ПриватБанку: {e}")
        return None
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Помилка обробки даних від API ПриватБанку: {e}")
        return None


# Додаємо функцію, яка буде повертати курси з вказаного джерела
def get_rates(source="monobank", cached=True):
    """Отримує курси валют з вказаного джерела.

    Args:
        source: Джерело курсів ('monobank' або 'privatbank').
        cached: Чи використовувати кешування.

    Returns:
        Словник з курсами валют або None, якщо сталася помилка.
    """
    if source == "monobank":
        return get_monobank_rates(cached)
    elif source == "privatbank":
        return get_privatbank_rates(cached)
    else:
        return None