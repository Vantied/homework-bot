class SendingFailed(Exception):
    """Ошибка при отправке сообщения в Telegram."""

    def __init__(self, message: str):
        """Инициализация."""
        super().__init__(message)


class BadEndpoint(Exception):
    """Эндпоинт API недоступен или вернул некорректный ответ."""

    def __init__(self, message: str):
        """Инициализация."""
        super().__init__(message)
