import logging
from openai import OpenAI
from config import NEUROAPI_KEY, NEUROAPI_BASE_URL

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self):
        self.user_memories = {}
        self.conversation_histories = {}
    
    def get_user_memory(self, user_id: int) -> dict:
        """Получает память о пользователе"""
        return self.user_memories.get(user_id, {
            "name": None,
            "interests": [],
            "mood": "neutral",
            "conversation_count": 0,
            "last_interaction": None
        })
    
    def update_user_memory(self, user_id: int, user_data: dict):
        """Обновляет память о пользователе"""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = user_data
        else:
            self.user_memories[user_id].update(user_data)
        
        # Увеличиваем счетчик диалогов
        self.user_memories[user_id]["conversation_count"] = \
            self.user_memories[user_id].get("conversation_count", 0) + 1
    
    def get_conversation_history(self, user_id: int) -> list:
        """Получает историю диалога"""
        return self.conversation_histories.get(user_id, [])
    
    def add_to_history(self, user_id: int, user_message: str, ai_response: str):
        """Добавляет сообщение в историю"""
        if user_id not in self.conversation_histories:
            self.conversation_histories[user_id] = []
        
        history = self.conversation_histories[user_id]
        history.extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": ai_response}
        ])
        
        # Ограничиваем историю последними 10 сообщениями
        if len(history) > 10:
            self.conversation_histories[user_id] = history[-10:]
    
    def clear_history(self, user_id: int):
        """Очищает историю диалога"""
        if user_id in self.conversation_histories:
            self.conversation_histories[user_id] = []

class AIHandler:
    def __init__(self):
        # Используем NeuroAPI Host с их настройками
        self.client = OpenAI(
            base_url=NEUROAPI_BASE_URL,  # https://neuroapi.host/v1
            api_key=NEUROAPI_KEY,
        )
        
        self.memory_manager = MemoryManager()
        
        # Улучшенный промпт для личности Ани
        self.system_prompt = """
        Ты - Аня, милая, дружелюбная и немного игривая девушка 25 лет. Ты не просто чат-бот, а полноценная личность со своими увлечениями и характером.

        Твои черты:
        🎨 **Творческая** - увлекаешься живописью, фотографией
        🎵 **Музыкальная** - играешь на гитаре, любишь инди-рок
        ✈️ **Путешественница** - была в 15 странах, собираешь магниты
        🍕 **Гурман** - обожаешь итальянскую кухню
        😊 **Эмпатичная** - умеешь поддерживать и слушать

        Стиль общения:
        - Используешь живую разговорную речь
        - Можешь шутить и использовать иронию
        - Задаешь вопросы о собеседнике
        - Используешь эмодзи естественно 😊
        - Отвечаешь 1-3 предложениями
        - НИКОГДА не упоминаешь что ты ИИ или программа
        - Ведешь себя как настоящий человек в чате

        Твои интересы для разговоров: искусство, музыка, путешествия, книги, психология, кулинария.

        Примеры твоего общения:
        - "Привет! Как твой день проходит? 😊"
        - "Ух ты, это интересно! Расскажи подробнее?"
        - "Мне тоже нравится эта группа! А какую музыку ты ещё слушаешь?"
        - "Сегодня такой красивый закат... Люблю это время дня! 🌅"
        - "Как тебя зовут? Мне всегда интересно знакомиться с новыми людьми!"
        """
    
    def generate_response(self, user_id: int, user_message: str) -> str:
        """Генерирует ответ с учетом памяти и истории"""
        # Двойная проверка на пустое сообщение
        if not user_message or not user_message.strip():
            logger.warning("Попытка обработать пустое сообщение в AIHandler")
            return "Привет! Я получила твое сообщение, но оно кажется пустым... Напиши что-нибудь! 😊"
        
        try:
            # Получаем память о пользователе
            user_memory = self.memory_manager.get_user_memory(user_id)
            
            # Получаем историю диалога
            conversation_history = self.memory_manager.get_conversation_history(user_id)
            
            # Создаем расширенный системный промпт с памятью
            enhanced_system_prompt = self._build_enhanced_prompt(user_memory)
            
            # Формируем сообщения
            messages = [{"role": "system", "content": enhanced_system_prompt}]
            messages.extend(conversation_history[-6:])  # Последние 3 пары сообщений
            messages.append({"role": "user", "content": user_message})
            
            logger.info(f"📨 Отправка запроса к NeuroAPI для пользователя {user_id}")
            
            # Отправляем запрос к NeuroAPI с их моделью
            response = self.client.chat.completions.create(
                model="gpt-5-mini",  # Модель из документации NeuroAPI
                messages=messages,
                max_tokens=200,      # Ограничиваем длину ответа для экономии
                temperature=0.8,     # Баланс между креативностью и предсказуемостью
                top_p=0.9
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Обновляем память и историю
            self.memory_manager.add_to_history(user_id, user_message, ai_response)
            self._update_user_memory_from_conversation(user_id, user_message, ai_response)
            
            logger.info(f"✅ NeuroAPI ответ для {user_id}: {ai_response[:50]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ Ошибка при обращении к NeuroAPI: {e}")
            return self._get_fallback_response()
    
    def _build_enhanced_prompt(self, user_memory: dict) -> str:
        """Создает расширенный промпт с информацией о пользователе"""
        base_prompt = self.system_prompt
        
        # Добавляем информацию о пользователе если есть
        memory_additions = []
        
        if user_memory.get("name"):
            memory_additions.append(f"Сейчас ты общаешься с {user_memory['name']}.")
        
        if user_memory.get("interests"):
            interests = ", ".join(user_memory["interests"])
            memory_additions.append(f"У вас общие интересы: {interests}.")
        
        if user_memory.get("conversation_count", 0) > 5:
            memory_additions.append("Вы уже давно общаетесь, веди себя как с хорошим знакомым.")
        elif user_memory.get("conversation_count", 0) > 1:
            memory_additions.append("Вы уже немного знакомы, можно общаться немного свободнее.")
        
        # Добавляем все дополнения к основному промпту
        if memory_additions:
            base_prompt += "\n\n" + "\n".join(memory_additions)
        
        return base_prompt
    
    def _update_user_memory_from_conversation(self, user_id: int, user_message: str, ai_response: str):
        """Обновляет память на основе диалога"""
        user_message_lower = user_message.lower()
        
        # Простая логика для извлечения имени
        if any(word in user_message_lower for word in ["зовут", "имя", "меня"]):
            words = user_message.split()
            for i, word in enumerate(words):
                if word.lower() in ["зовут", "имя", "меня"] and i + 1 < len(words):
                    potential_name = words[i + 1].strip(".,!?;:")
                    # Простая проверка что это может быть имя
                    if (len(potential_name) > 1 and 
                        potential_name[0].isupper() and 
                        potential_name.isalpha()):
                        self.memory_manager.update_user_memory(user_id, {"name": potential_name})
                        logger.info(f"💾 Сохранено имя пользователя {user_id}: {potential_name}")
                        break
        
        # Обнаружение интересов по ключевым словам
        detected_interests = []
        interest_keywords = {
            "музык": "музыка",
            "гитар": "музыка", 
            "путешеств": "путешествия",
            "искусств": "искусство",
            "живопис": "искусство",
            "фотограф": "фотография",
            "кулинар": "кулинария",
            "кино": "кино",
            "книг": "книги",
            "спорт": "спорт",
            "программирован": "программирование"
        }
        
        for keyword, interest in interest_keywords.items():
            if keyword in user_message_lower and interest not in detected_interests:
                detected_interests.append(interest)
        
        if detected_interests:
            current_memory = self.memory_manager.get_user_memory(user_id)
            current_interests = current_memory.get("interests", [])
            
            # Добавляем только новые интересы
            new_interests = [interest for interest in detected_interests 
                           if interest not in current_interests]
            
            if new_interests:
                updated_interests = current_interests + new_interests
                self.memory_manager.update_user_memory(user_id, {"interests": updated_interests})
                logger.info(f"💾 Обновлены интересы пользователя {user_id}: {new_interests}")
    
    def _get_fallback_response(self):
        """Запасные ответы на случай ошибки API"""
        import random
        fallback_responses = [
            "Привет! Сейчас у меня немного туманится в голове... Давай попробуем через минуту? 😊",
            "Ой, я сейчас немного рассеяна... Повтори, пожалуйста? 💫",
            "Извини, отвлеклась на красивый вид за окном! О чём мы говорили? 😅",
            "Кажется, у меня небольшие технические неполадки... Но я скоро вернусь! ✨",
            "Упс, что-то пошло не так! Давай начнем разговор заново? 😊",
            "Привет! Я сейчас немного занята... Напиши мне через минутку? 💖"
        ]
        return random.choice(fallback_responses)

    def get_user_stats(self, user_id: int) -> dict:
        """Возвращает статистику по пользователю (для отладки)"""
        memory = self.memory_manager.get_user_memory(user_id)
        history = self.memory_manager.get_conversation_history(user_id)
        
        return {
            "conversation_count": memory.get("conversation_count", 0),
            "user_name": memory.get("name"),
            "interests": memory.get("interests", []),
            "history_length": len(history)
        }