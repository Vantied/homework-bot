class BadEndPoint(Exception):
    """Эндпоинт API недоступен или вернул некорректный ответ."""

    pass


class InvalidJSONResponse(Exception):
    """Ошибка при парсинге ответа от API."""

    pass


class ApiRequestError(Exception):
    """Ошибка, возникающая при ошибке запроса к API."""

    pass


class ResponseStructureError(Exception):
    """Ошибка, возникающая при нарушении структуры ответа."""

    pass
