class Translations:
    _messages = {
        'uk': {
            'start': 'Вітаю! Я віртуальний помічник факультету інформатики та обчислювальної техніки КПІ. Надішліть '
                     'мені повідомлення з питанням, що вас цікавить, і я відповім використовуючи RAG систему.',
            'help': 'Просто надішліть повідомлення з питанням, що вас цікавить. Використайте /reset або /start щоб '
                    'очистити історію розмови.',
            'reset': 'Історію розмови очищено.',
            'error': 'Вибачте, сталася помилка під час обробки вашого запиту.'
        }
    }

    @classmethod
    def get(cls, key: str, lang: str = 'uk') -> str:
        return cls._messages.get(lang, {}).get(key, key)
