# Telegram-бот для отслеживания статуса проверки работ

Бот раз в 10 минут опрашивает API Яндекс Практикума и присылает сообщение в Telegram, когда меняется статус проверки домашней работы: взята на ревью, принята или возвращена на доработку.

## Возможности

- При старте бот проверяет, что все токены заданы; если какого-то нет, не запускается и пишет об этом в лог.
- Обрабатывает недоступность API, неожиданные коды ответа и некорректный JSON с помощью собственных исключений.
- Проверяет структуру ответа и сам статус работы.
- Пишет логи в stdout и сообщает об ошибках в Telegram — по одному сообщению на ошибку, без спама повторами.
- Procfile для запуска на хостинге.

## Технологии

Python 3.10+, pyTelegramBotAPI, requests, python-dotenv, pytest.

## Как запустить

```bash
git clone https://github.com/Vantied/homework-bot.git
cd homework-bot
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Создайте файл `.env`:

```env
PRACTICUM_TOKEN=your_practicum_token
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

```bash
python homework.py
```

## Что я вынес из проекта

- Работа с внешним API и устойчивость к его сбоям.
- Логирование и уведомления для сервиса, который работает без присмотра.

## Автор

Иван Богатов — [GitHub](https://github.com/Vantied) · Telegram [@Ivan_bogatov55](https://t.me/Ivan_bogatov55)
