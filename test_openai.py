#!/usr/bin/env python3
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_openai_key():
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY не найден в .env файле")
        return False
    
    if not api_key.startswith('sk-'):
        print("❌ Ключ должен начинаться с 'sk-'")
        return False
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Простой тестовый запрос
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Привет! Ответь коротко 'Тест пройден!'"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ Ключ рабочий! Ответ ИИ: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании ключа: {e}")
        return False

if __name__ == '__main__':
    test_openai_key()