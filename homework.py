import logging
import os
import sys
import time

import requests
from dotenv import load_dotenv
from telebot import TeleBot
import exceptions_customs


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
    Проверяет все переменные, и если хоть одного нет, то вернёт False.
    Если все переменные есть, то вернёт True.
    Напишет в логах все недостающие переменные.
    """
    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN
    }
    missing_tokens = [name for name, token in tokens.items() if not token]
    if missing_tokens:
        for name in missing_tokens:
            logger.critical(f'Отсутсвует ключ {name}')
        return False
    return True


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
        logger.debug(f'Успешное отправление сообщения {message}')
    except Exception as error:
        logger.debug(f'Не получилось отправить сообщение: {error}')
        raise exceptions_customs.SendingFailed(
            f'Не получилось отправить сообщение {error}'
        )


def get_api_answer(timestamp):
    """
    Функция для получения ответа от API.
    Если что-то пошло не так — вызовет соответствующее исключение.
    """
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException as error:
        logger.error(f'Сбой при запросе к эндпоинту {ENDPOINT} {error}')
        raise exceptions_customs.ApiRequestError(
            f'Ошибка при запросе API {error}'
        )

    if response.status_code != 200:
        logger.error(f'Недоступность эндпоинта: {ENDPOINT}')
        raise exceptions_customs.BadEndpoint(
            f'Эндпоинт недоступен. Код ответа: {response.status_code}'
        )

    return response.json()


def check_response(response):
    """
    Функция проверяет соответствие документации.
    Выбросит исключение если не будет ответ не будет совподать с документацией.
    Напишет об проблемах в логах.
    """
    # Проверяется, что response действительно словарь
    if not isinstance(response, dict):
        logger.error('Отсутвие получние словаря при запросе к API')
        raise TypeError('Ответ не является словарём')
    # Проверка наличия ключа 'homeworks'
    if 'homeworks' not in response:
        logger.error('Отсутсвует ключ "homeworks"')
        raise KeyError('Отсутсвует ключ "homeworks"')
    # Проверяется, что homeworks список
    if not isinstance(response.get('homeworks'), list):
        logger.error('"homeworks" должен быть списком')
        raise TypeError('"homeworks" должен быть списком')


def parse_status(homework):
    """
    Извлекает статус одной домашней работы.
    Возвращает сообщение
    """
    if homework.get('homework_name') is None:
        logger.error('Отсутвсует ключ "homework_name"')
        raise KeyError('Отсутвсует ключ "homework_name"')
    # Получение ключей
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    # Проверка известных статусов
    if status not in HOMEWORK_VERDICTS:
        logger.error(
            f'Неожиданный статус домашней работы: {status}'
        )
        raise ValueError(f'Неизвестный статус: {status}')
    verdict = HOMEWORK_VERDICTS.get(f'{status}')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise SystemExit('Отсутвуют переменные окружения')

    # Создаем объект класса бота
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    # Переменная, сохраняет предыдущий статус, чтобы его заново не оптравлять
    last_message = ''
    # Переменная, сохраняет предыдущую ошибку, чтобы его заново не оптравлять
    last_error_message = ''

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
                if message != last_message:
                    send_message(bot, message)
                    last_message = message
            else:
                logger.debug(
                    'В ответе API получен пустой список домашних работ'
                )
            timestamp = response.get('current_date', timestamp)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if message != last_error_message:
                try:
                    send_message(bot, message)
                    last_error_message = message
                    logger.info('Отправлено уведомление об ошибке')
                except Exception as error:
                    logger.error(
                        f'Не удалось отправить сообщение об ошибке: {error}'
                    )

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
