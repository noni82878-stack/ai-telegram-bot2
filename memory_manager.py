import json
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self):
        self.user_memories = {}
        self.conversation_histories = {}
    
    def get_user_memory(self, user_id: int) -> Dict:
        """Получает память о пользователе"""
        return self.user_memories.get(user_id, {
            "name": None,
            "interests": [],
            "mood": "neutral",
            "conversation_count": 0
        })
    
    def update_user_memory(self, user_id: int, user_data: Dict):
        """Обновляет память о пользователе"""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = user_data
        else:
            self.user_memories[user_id].update(user_data)
        
        # Увеличиваем счетчик диалогов
        self.user_memories[user_id]["conversation_count"] = \
            self.user_memories[user_id].get("conversation_count", 0) + 1
    
    def get_conversation_history(self, user_id: int) -> List:
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