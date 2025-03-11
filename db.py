# db.py
import sqlite3

# Підключення до бази даних (або її створення)
conn = sqlite3.connect('currency_bot.db', check_same_thread=False)
cursor = conn.cursor()

# Створення таблиці (виконується тільки якщо таблиці ще немає)
def create_tables():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            from_currency TEXT NOT NULL,
            to_currency TEXT NOT NULL,
            converted_amount REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

def add_conversion(chat_id, amount, from_currency, to_currency, converted_amount):
    """Додає запис про конвертацію в базу даних."""
    cursor.execute("""
        INSERT INTO conversions (chat_id, amount, from_currency, to_currency, converted_amount, timestamp)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (chat_id, amount, from_currency, to_currency, converted_amount))
    conn.commit()

def get_history(chat_id, limit=10):
    """Отримує історію конвертацій для заданого chat_id.

    Args:
        chat_id: ID чату.
        limit: Максимальна кількість записів для повернення.

    Returns:
        Список кортежів з даними про конвертації, або порожній список,
        якщо історія порожня.
    """
    cursor.execute("""
        SELECT amount, from_currency, to_currency, converted_amount, timestamp
        FROM conversions
        WHERE chat_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (chat_id, limit))  # Використовуємо параметризований запит і для limit
    return cursor.fetchall()

# При запуску модуля одразу створюємо таблиці, якщо їх немає.
create_tables()