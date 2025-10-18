import logging
import os
import requests

from dotenv import load_dotenv
from telebot import TeleBot, types

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN ')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

# Конфигурация логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


def check_tokens():
    """
    Функция для проверки доступности переменных окружений
    Если хоть одной нет вернёт значние 1
    Если всё есть, то вернёт значение 0
    """
    if PRACTICUM_TOKEN is None:
        return 1
    if TELEGRAM_CHAT_ID is None:
        return 1
    if TELEGRAM_TOKEN is None:
        return 1
    return 0


def send_message(bot, message):
    ...


def get_api_answer(timestamp):
    """
    Функция для получения ответа от сайта
    Если что-то пошло не так, вызовит ошибку
    """
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        response = response.json()
        return response
    except Exception as error:
        raise error(f'Ошибка при запросе API {error}')


def check_response(response):
    """Функция проверяет соответствие документации"""
    # Проверяется, response действительно ли словарь
    if not isinstance(response, dict):
        raise TypeError('Ответ не является словарём')
    # Проверка наличия ключа 'homeworks'
    if 'homeworks' not in response:
        raise KeyError('Отсутсвует ключ "homeworks"')


def parse_status(homework):
    homework_name = homework.get('homework_name')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    ...

    # Создаем объект класса бота
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    ...

    while True:
        try:

            ...

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
        ...


if __name__ == '__main__':
    main()
