#!/usr/bin/env python3
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_neuroapi():
    """Тестируем подключение к NeuroAPI"""
    api_key = os.getenv('NEUROAPI_KEY')
    
    if not api_key:
        print("❌ NEUROAPI_KEY не найден в .env файле")
        return False
    
    try:
        client = OpenAI(
            base_url="https://neuroapi.host/v1",
            api_key=api_key,
        )
        
        print("🔄 Тестируем NeuroAPI...")
        
        # Тестовый запрос как в документации
        completion = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "user", "content": "Привет! Ответь коротко 'НейроAPI работает отлично!'"}
            ],
            max_tokens=50
        )
        
        result = completion.choices[0].message.content
        print(f"✅ NeuroAPI работает! Ответ: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка NeuroAPI: {e}")
        return False

if __name__ == '__main__':
    test_neuroapi()