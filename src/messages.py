"""Bot messages - all text messages in one place"""


class BotMessages:
    """All bot text messages as constants"""

    # Command responses
    WELCOME = (
        "👋 Привет! Я LLM-бот помощник.\n\n"
        "Я могу помочь вам с различными вопросами и задачами.\n\n"
        "Используйте /help для просмотра доступных команд."
    )

    HELP = (
        "📚 Доступные команды:\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n"
        "/role - Показать текущую роль ассистента\n"
        "/reset - Очистить историю диалога\n\n"
        "Просто отправьте мне сообщение, и я постараюсь помочь!"
    )

    RESET_SUCCESS = "🔄 История диалога очищена. Начнем сначала!"
    RESET_NO_CONTEXT = "⚠️ Управление контекстом не настроено."

    ROLE_INFO = "🎭 Текущая роль ассистента:\n\n{role_description}"

    # Error messages
    NO_LLM = "LLM не настроен. Обратитесь к администратору."

    ERROR_CONNECTION = (
        "⚠️ Не удалось подключиться к сервису ИИ.\nПожалуйста, попробуйте через несколько минут."
    )

    ERROR_TIMEOUT = "⏱️ Превышено время ожидания ответа.\nПопробуйте отправить сообщение еще раз."

    ERROR_RATE_LIMIT = (
        "🚫 Превышен лимит запросов к сервису ИИ.\n"
        "Пожалуйста, подождите немного перед следующим запросом."
    )

    ERROR_API = "❌ Ошибка сервиса ИИ.\nПопробуйте позже или обратитесь к администратору."

    ERROR_LLM = (
        "😔 Произошла ошибка при обработке вашего сообщения.\nПожалуйста, попробуйте еще раз."
    )

    ERROR_UNEXPECTED = "😔 Произошла непредвиденная ошибка.\nПожалуйста, попробуйте позже."

    @staticmethod
    def error(error_type: str) -> str:
        """Get error message by type

        Args:
            error_type: Type of error (connection, timeout, rate_limit, api, llm, unexpected)

        Returns:
            Error message string
        """
        error_messages = {
            "no_llm": BotMessages.NO_LLM,
            "connection": BotMessages.ERROR_CONNECTION,
            "timeout": BotMessages.ERROR_TIMEOUT,
            "rate_limit": BotMessages.ERROR_RATE_LIMIT,
            "api": BotMessages.ERROR_API,
            "llm": BotMessages.ERROR_LLM,
            "unexpected": BotMessages.ERROR_UNEXPECTED,
        }
        return error_messages.get(error_type, BotMessages.ERROR_UNEXPECTED)
