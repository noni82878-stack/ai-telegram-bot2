import os
import logging
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Проверка токенов
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден в .env файле")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY не найден в .env файле")

# Проверка формата OpenAI ключа
if not OPENAI_API_KEY.startswith('sk-'):
    logging.warning("⚠️  OpenAI API ключ может быть неверным (должен начинаться с 'sk-')")

# Безопасная проверка ключа (логируем только начало и конец)
if OPENAI_API_KEY:
    key_preview = f"{OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-4:]}"
    logging.info(f"🔑 OpenAI API ключ загружен: {key_preview}")
else:
    logging.error("❌ OpenAI API ключ не загружен")