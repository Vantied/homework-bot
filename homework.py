import logging
import os
import sys
import time
import json

import requests
from dotenv import load_dotenv
from telebot import TeleBot
from telebot import apihelper
import exceptions


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
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
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """
    Функция для проверки доступности переменных окружений.
    Вернёт список пропущенных токенов.
    Если нет пропущенных токенов, вернёт пустой список.
    """
    tokens = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']
    missing_tokens = [key for key in tokens if not globals().get(key)]
    return missing_tokens


def send_message(bot, message):
    """
    Отправка сообщений.
    Напишет в логах о успешном или не успешном отправление сообщения.
    """
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f'{message}'
        )
    except apihelper.ApiException as error:
        logger.error(f'Не получилось отправить сообщение: {error}')
    else:
        logger.debug(f'Успешное отправление сообщения {message}')


def get_api_answer(timestamp):
    """
    Функция для получения ответа от API.
    Если что-то пошло не так — вызовет соответствующее исключение.
    """
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        if response.status_code != 200:
            raise exceptions.BadEndPoint(
                f'Эндпоинт недоступен. Код ответа: {response.status_code}'
            )
        return response.json()

    except requests.RequestException as error:
        raise exceptions.ApiRequestError(f'Ошибка при запросе API: {error}')

    except json.decoder.JSONDecodeError as error:
        raise exceptions.InvalidJSONResponse(
            f'Ошибка при разборе JSON ответа от API: {error}'
        )


def check_response(response):
    """
    Функция проверяет соответствие документации.
    Выбросит исключение если не будет ответ совподать с документацией.
    """
    # Проверяется, что response действительно словарь
    if not isinstance(response, dict):
        raise TypeError('Ответ не является словарём')
    # Проверка наличия ключа 'homeworks'
    if 'homeworks' not in response:
        raise KeyError('Отсутсвует ключ "homeworks"')
    # Проверяется, что homeworks список
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('"homeworks" должен быть списком')
    # Проверяется, что current_date есть
    if 'current_date' not in response:
        raise exceptions.ResponseStructureError(
            'Ключ "current_date" отсутствует в ответе от API'
        )
    else:
        current_date = response.get('current_date')
        # Проверяется, что current_date это int
        if not isinstance(current_date, int):
            raise exceptions.ResponseStructureError(
                '"current_date" должен быть int'
            )


def parse_status(homework):
    """
    Извлекает статус одной домашней работы.
    Возвращает сообщение.
    """
    if homework.get('homework_name') is None:
        raise KeyError('Отсутвсует ключ "homework_name"')
    # Получение ключей
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    # Проверка известных статусов
    if status not in HOMEWORK_VERDICTS:
        raise ValueError(f'Неизвестный статус: {status}')
    verdict = HOMEWORK_VERDICTS.get(f'{status}')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def send_messange_if_change(bot, message, last_message):
    """
    Отправка сообщения только если оно отличается от последнего.
    Возвращает новое значение последнего сообщения.
    """
    if message != last_message:
        send_message(bot, message)
    return message


def main():
    """Основная логика работы бота."""
    missing_tokens = check_tokens()
    if missing_tokens:
        logger.critical(
            f'Отсутсвуют переменные окружения: {", ".join(missing_tokens)}'
        )
        raise SystemExit('Отсутвуют переменные окружения')

    # Создаем объект класса бота
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    # Переменная, сохраняет предыдущий статус, чтобы его заново не оптравлять
    last_message = ''

    while True:
        try:
            # Получаем ответ
            response = get_api_answer(timestamp)
            # Проверяем ответ на корректоность
            check_response(response)
            homeworks = response.get('homeworks')
            if homeworks:
                homework = homeworks[0]
                message = parse_status(homework)
                last_message = send_messange_if_change(
                    bot, message, last_message
                )
            else:
                logger.debug(
                    'В ответе API получен пустой список домашних работ'
                )
            timestamp = response.get('current_date', timestamp)

        except exceptions.ResponseStructureError as error:
            logger.error(error)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            last_message = send_messange_if_change(
                bot, message, last_message
            )
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
