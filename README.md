# Currency Converter Telegram Bot

Telegram bot for converting currencies using up-to-date exchange rates from Monobank and PrivatBank APIs. Supports multiple currencies, inline mode, conversion history, and source selection.

**Telegram Bot:** [@Converter_tutorial1_bot](https://t.me/Converter_tutorial1_bot)
**GitHub:** [AlexKushch-sys](https://github.com/AlexKushch-sys)

## Features

*   Currency conversion using real-time exchange rates from Monobank and PrivatBank.
*   Support for multiple currencies (USD, EUR, UAH, GBP, PLN, and easily extensible).
*   User-friendly interface with custom Telegram keyboards.
*   Inline mode for quick conversions in any chat.
*   Conversion history stored locally using SQLite.
*   Choice of exchange rate source (Monobank or PrivatBank).
*   Error handling and input validation.
*   Caching of exchange rates.
*   Easy setup.
*   Modular code.

## Requirements

*   Python 3.7+
*   `pyTelegramBotAPI`
*   `requests`
*   `python-dotenv`
*   `sqlite3` (usually comes pre-installed with Python)

## Installation

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/AlexKushch-sys/Currency-Converter-Telegram-Bot.git](https://www.google.com/search?q=https://github.com/AlexKushch-sys/Currency-Converter-Telegram-Bot.git)
    cd Currency-Converter-Telegram-Bot
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    ```

3.  **Activate the virtual environment:**

    *   **Windows:**
        ```bash
        venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Create a `.env` file:** Create a file named `.env` in the root directory of the project and add the following:

    ```
    TOKEN=YOUR_TELEGRAM_BOT_TOKEN
    MONOBANK_API_URL=[https://api.monobank.ua/bank/currency](https://api.monobank.ua/bank/currency)
    ```

    Replace `YOUR_TELEGRAM_BOT_TOKEN` with your actual Telegram bot token (obtained from @BotFather).

6.  **Run the bot:**

    ```bash
    python main.py
    ```

## Usage

*   `/start`: Starts the bot and displays the main menu.
*   `/help`: Displays help information.
*   `/convert`: Starts the currency conversion process.
*   `/rates`: Displays current exchange rates.
*   `/history`: Shows the history of your conversions.
*   `/source`: Allows you to select the source for exchange rates (Monobank or PrivatBank).
*   **Inline Mode:** Type `@Converter_tutorial1_bot <amount> <from_currency> to <to_currency>` in any chat. For example: `@Converter_tutorial1_bot 100 USD to UAH`.

## Contributing

Feel free to submit pull requests or open issues to improve the bot.

## License

This project is open-source (add a license here if you like, e.g., MIT).