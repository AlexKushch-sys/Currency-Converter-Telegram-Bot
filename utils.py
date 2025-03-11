# utils.py

def get_currency_name(code, source="monobank"):
    """Повертає назву валюти за її кодом, або за назвою (для ПриватБанку).

    Args:
        code: Код валюти (ISO 4217) або назва валюти.
        source: Джерело даних ('monobank' або 'privatbank').
    Returns:
        Назва валюти (str) або оригінальний код/назва, якщо не знайдено.
    """
    currency_names_monobank = {
        840: "USD", 978: "EUR", 980: "UAH", 826: "GBP", 985: "PLN",
        # ... інші валюти ...
    }
    currency_names_privatbank = {  # Для ПриватБанку використовуємо назви
        "USD": "USD",
        "EUR": "EUR",
        "UAH": "UAH",
        "GBP": "GBP",
        "PLN": "PLN",
        "BTC": "BTC" #ПриватБанк дає курс BTC
    }

    if source == "monobank":
        return currency_names_monobank.get(code, str(code))
    elif source == "privatbank":
        return currency_names_privatbank.get(code, code)
    else:
        return str(code) #Або повертати помилку