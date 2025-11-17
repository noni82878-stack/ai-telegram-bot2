import logging
import time
import random
from openai import OpenAI
from config import NEUROAPI_KEY, NEUROAPI_BASE_URL

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self):
        self.user_memories = {}
        self.conversation_histories = {}
    
    def get_user_memory(self, user_id: int) -> dict:
        return self.user_memories.get(user_id, {
            "name": None,
            "interests": [],
            "mood": "neutral",
            "conversation_count": 0,
        })
    
    def update_user_memory(self, user_id: int, user_data: dict):
        if user_id not in self.user_memories:
            self.user_memories[user_id] = user_data
        else:
            self.user_memories[user_id].update(user_data)
        self.user_memories[user_id]["conversation_count"] = \
            self.user_memories[user_id].get("conversation_count", 0) + 1
    
    def get_conversation_history(self, user_id: int) -> list:
        return self.conversation_histories.get(user_id, [])
    
    def add_to_history(self, user_id: int, user_message: str, ai_response: str):
        if user_id not in self.conversation_histories:
            self.conversation_histories[user_id] = []
        history = self.conversation_histories[user_id]
        history.extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": ai_response}
        ])
        if len(history) > 8:  # Уменьшили историю для экономии токенов
            self.conversation_histories[user_id] = history[-8:]
    
    def clear_history(self, user_id: int):
        if user_id in self.conversation_histories:
            self.conversation_histories[user_id] = []

class AIHandler:
    def __init__(self):
        self.client = OpenAI(
            base_url=NEUROAPI_BASE_URL,
            api_key=NEUROAPI_KEY,
        )
        self.memory_manager = MemoryManager()
        
        # Упрощенный промпт для экономии токенов
        self.system_prompt = """
        Ты - Аня, дружелюбная девушка 25 лет. Общаешься неформально, используешь эмодзи.
        Интересуешься искусством, музыкой, путешествиями. Отвечай кратко (1-2 предложения).
        Не упоминай что ты ИИ. Веди себя как настоящий человек.
        """
    
    def generate_response(self, user_id: int, user_message: str) -> str:
        if not user_message or not user_message.strip():
            return "Привет! Напиши что-нибудь, и я с радостью отвечу! 😊"
        
        # Ограничиваем длину сообщения для экономии токенов
        if len(user_message) > 500:
            user_message = user_message[:500] + "..."
        
        try:
            user_memory = self.memory_manager.get_user_memory(user_id)
            conversation_history = self.memory_manager.get_conversation_history(user_id)
            
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(conversation_history[-4:])  # Уменьшили историю
            messages.append({"role": "user", "content": user_message})
            
            # Упрощенный запрос без проблемных параметров
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",  # Пробуем стабильную модель
                messages=messages,
                max_tokens=120,  # Уменьшили длину ответа
                temperature=0.7  # Убрали top_p
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Обновляем память
            self.memory_manager.add_to_history(user_id, user_message, ai_response)
            
            logger.info(f"✅ Успешный ответ NeuroAPI для {user_id}")
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ Ошибка NeuroAPI: {e}")
            return self._get_smart_fallback(user_message)
    
    def _get_smart_fallback(self, user_message: str) -> str:
        """Умные запасные ответы на основе типа сообщения"""
        user_message_lower = user_message.lower()
        
        # Ответы в зависимости от содержания сообщения
        if any(word in user_message_lower for word in ['привет', 'хай', 'здравствуй']):
            return "Привет-привет! 😊 Как твои дела?"
        elif any(word in user_message_lower for word in ['как дела', 'как ты']):
            return "Всё хорошо, спасибо! А у тебя как? 🌟"
        elif any(word in user_message_lower for word in ['пока', 'до свидания']):
            return "Пока! Было приятно пообщаться! 👋"
        elif any(word in user_message_lower for word in ['люблю', 'нравишься']):
            return "Ты такой милый! Мне тоже нравится с тобой общаться 💕"
        elif any(word in user_message_lower for word in ['имя', 'зовут']):
            return "Меня зовут Аня! А тебя? 😊"
        elif any(word in user_message_lower for word in ['музык', 'песн', 'гитар']):
            return "Обожаю музыку! Сейчас слушаю инди-рок. А ты какую музыку любишь? 🎵"
        elif any(word in user_message_lower for word in ['путешеств', 'поездк', 'отпуск']):
            return "Обожаю путешествия! Недавно вернулась из Грузии - там невероятно! ✈️"
        elif any(word in user_message_lower for word in ['искусств', 'рисун', 'картин']):
            return "Люблю искусство! Особенно импрессионистов. А ты разбираешься в искусстве? 🎨"
        else:
            # Случайные общие ответы
            general_responses = [
                "Интересно! Расскажи подробнее? 😊",
                "Ух ты! А что ещё тебя интересует?",
                "Классно! Давай поговорим об этом?",
                "Любопытно! А что ты сам об этом думаешь?",
                "Забавно! Продолжай, мне нравится 🎉"
            ]
            return random.choice(general_responses)