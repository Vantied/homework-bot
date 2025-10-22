class SendingFailed(Exception):
    """Ошибка при отправке сообщения в Telegram."""

    pass


class BadEndPoint(Exception):
    """Эндпоинт API недоступен или вернул некорректный ответ."""

    pass


class InvalidJSONResponse(Exception):
    """Ошибка при парсинге ответа от API."""

    pass


class ApiRequestError(Exception):
    """Ошибка, возникающее при ошибке запроса к API."""

    pass
