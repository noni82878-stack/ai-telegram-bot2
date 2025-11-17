import os
import logging
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
NEUROAPI_KEY = os.getenv('NEUROAPI_KEY')
NEUROAPI_BASE_URL = "https://neuroapi.host/v1"

# Проверка токенов
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден в .env файле")

if not NEUROAPI_KEY:
    raise ValueError("❌ NEUROAPI_KEY не найден в .env файле")

# Безопасная проверка ключа
if NEUROAPI_KEY:
    key_preview = f"{NEUROAPI_KEY[:8]}...{NEUROAPI_KEY[-4:]}"
    logging.info(f"🔑 NeuroAPI ключ загружен: {key_preview}")
    logging.info(f"🌐 NeuroAPI URL: {NEUROAPI_BASE_URL}")