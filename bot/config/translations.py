class Translations:
    _messages = {
        'uk': {
            'start': 'Вітаю! Я ваш бот. Надішліть мені повідомлення, і я відповім використовуючи RAG систему.',
            'help': 'Просто надішліть повідомлення. Використайте /reset щоб очистити історію розмови.',
            'reset': 'Історію розмови очищено.',
            'error': 'Вибачте, сталася помилка під час обробки вашого запиту.'
        }
    }

    @classmethod
    def get(cls, key: str, lang: str = 'uk') -> str:
        return cls._messages.get(lang, {}).get(key, key)
