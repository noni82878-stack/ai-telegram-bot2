import os
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
NEUROAPI_KEY = os.environ.get('NEUROAPI_KEY')
NEUROAPI_BASE_URL = "https://neuroapi.host/v1"

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен")

if not NEUROAPI_KEY:
    raise ValueError("NEUROAPI_KEY не установлен")

logging.info("✅ Конфигурация загружена успешно")