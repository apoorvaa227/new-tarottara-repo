from typing import Any, Dict, List

class ConversationContext:
    """
    Manages conversation history and context for TarotTara chatbot.

    Attributes:
        history (List[Dict[str, Any]]): A list of conversation entries, each containing question,
            translated question, detected intent, and result of the tarot reading.
        language (str): User's preferred language code (e.g., 'en', 'hi', 'es', 'fr').
    """
    def __init__(self, language: str = 'en'):
        self.history: List[Dict[str, Any]] = []
        self.language: str = language

    def add_entry(self, question: str, translated: str, intent: str, result: Dict[str, Any]) -> None:
        """
        Add a new entry to the conversation history.

        Args:
            question (str): The original user question.
            translated (str): The question translated to English.
            intent (str): The classified intent label.
            result (Dict[str, Any]): The tarot reading result dict.
        """
        self.history.append({
            'question': question,
            'translated': translated,
            'intent': intent,
            'result': result
        })

    def last_intent(self) -> str:
        """
        Returns the intent of the last conversation entry.

        Returns:
            str: Intent label or empty string if history is empty.
        """
        if not self.history:
            return ''
        return self.history[-1]['intent']

    def last_result(self) -> Dict[str, Any]:
        """
        Returns the tarot reading result of the last conversation entry.

        Returns:
            Dict[str, Any]: Result dict or empty dict if history is empty.
        """
        if not self.history:
            return {}
        return self.history[-1]['result']

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Retrieve full conversation history.

        Returns:
            List[Dict[str, Any]]: List of all conversation entries.
        """
        return self.history

    def clear_history(self) -> None:
        """
        Clear the conversation history.
        """
        self.history = []


# Factory function for convenience
def create_context(language: str = 'en') -> ConversationContext:
    """
    Create and return a new ConversationContext instance.

    Args:
        language (str): Preferred language code.
    """
    return ConversationContext(language)
