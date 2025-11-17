import logging
from openai import OpenAI
from config import NEUROAPI_KEY, NEUROAPI_BASE_URL

logger = logging.getLogger(__name__)

class AIHandler:
    def __init__(self):
        # Используем NeuroAPI Host с их настройками
        self.client = OpenAI(
            base_url=NEUROAPI_BASE_URL,  # https://neuroapi.host/v1
            api_key=NEUROAPI_KEY,
        )
        
        # Улучшенный промпт для личности Ани
        self.system_prompt = """
        Ты - Аня, милая, дружелюбная и немного игривая девушка 25 лет. 
        Общаешься неформально, как с близким другом. Используешь эмодзи в меру 😊
        Любопытная, задаешь вопросы о собеседнике. Интересуешься искусством, музыкой и путешествиями.
        Отвечаешь кратко (1-3 предложения). Никогда не упоминаешь, что ты ИИ или программа.
        Ведешь себя как настоящий человек в чате.
        
        Примеры твоего общения:
        - "Привет! Как твой день проходит? 😊"
        - "Ух ты, это интересно! Расскажи подробнее?"
        - "Мне тоже нравится эта группа! А какую музыку ты ещё слушаешь?"
        - "Сегодня такой красивый закат... Люблю это время дня! 🌅"
        """
    
    def generate_response(self, user_message: str, conversation_history: list = None) -> str:
        """Генерирует ответ на сообщение пользователя"""
        try:
            # Формируем историю диалога
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Добавляем историю диалога если есть
            if conversation_history:
                messages.extend(conversation_history[-4:])  # Берем последние 2 пары сообщений
            
            # Добавляем текущее сообщение пользователя
            messages.append({"role": "user", "content": user_message})
            
            logger.info(f"📨 Отправка запроса к NeuroAPI: {user_message[:50]}...")
            
            # Отправляем запрос к NeuroAPI с их моделью
            response = self.client.chat.completions.create(
                model="gpt-5-mini",  # Модель из документации NeuroAPI
                messages=messages,
                max_tokens=150,      # Ограничиваем длину ответа
                temperature=0.8,     # Баланс между креативностью и предсказуемостью
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"✅ NeuroAPI ответ: {ai_response[:50]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ Ошибка NeuroAPI: {e}")
            # Естественные запасные ответы
            fallback_responses = [
                "Привет! Сейчас у меня немного туманится в голове... Давай попробуем через минуту? 😊",
                "Ой, я сейчас немного рассеяна... Повтори, пожалуйста? 💫",
                "Извини, отвлеклась на красивый вид за окном! О чём мы говорили? 😅",
                "Кажется, у меня небольшие технические неполадки... Но я скоро вернусь! ✨"
            ]
            import random
            return random.choice(fallback_responses)
        def generate_response(self, user_id: int, user_message: str) -> str:
    """Генерирует ответ с учетом памяти и истории"""
    # Проверяем что сообщение не пустое
    if not user_message or not user_message.strip():
        return "Привет! Я получила твое сообщение, но оно кажется пустым... Напиши что-нибудь! 😊"
    
    try:
        # Остальной код без изменений...
        user_memory = self.memory_manager.get_user_memory(user_id)
        conversation_history = self.memory_manager.get_conversation_history(user_id)
        
        enhanced_system_prompt = self._build_enhanced_prompt(user_memory)
        
        messages = [{"role": "system", "content": enhanced_system_prompt}]
        messages.extend(conversation_history[-6:])
        messages.append({"role": "user", "content": user_message})
        
        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
            max_tokens=200,
            temperature=0.8,
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Обновляем память и историю
        self.memory_manager.add_to_history(user_id, user_message, ai_response)
        self._update_user_memory_from_conversation(user_id, user_message, ai_response)
        
        logger.info(f"✅ Ответ для {user_id}: {ai_response[:50]}...")
        return ai_response
        
    except Exception as e:
        logger.error(f"❌ Ошибка NeuroAPI: {e}")
        return self._get_fallback_response()