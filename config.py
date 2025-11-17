import os
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем переменные окружения
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
NEUROAPI_KEY = os.environ.get('NEUROAPI_KEY')
NEUROAPI_BASE_URL = "https://neuroapi.host/v1"

# Проверка токенов с более информативными сообщениями
if not TELEGRAM_TOKEN:
    error_msg = """
❌ TELEGRAM_BOT_TOKEN не найден!

Как исправить:
1. Зайдите в настройки вашего хостинга (Render/Railway/etc)
2. Найдите раздел 'Environment Variables' или 'Переменные окружения'
3. Добавьте переменную: TELEGRAM_BOT_TOKEN = ваш_токен_от_BotFather
4. Перезапустите приложение
"""
    logger.error(error_msg)
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен")

if not NEUROAPI_KEY:
    error_msg = """
❌ NEUROAPI_KEY не найден!

Как исправить:
1. Зайдите в настройки вашего хостинга
2. Найдите раздел 'Environment Variables'
3. Добавьте переменную: NEUROAPI_KEY = ваш_ключ_от_neuroapi_host
4. Перезапустите приложение
"""
    logger.error(error_msg)
    raise ValueError("NEUROAPI_KEY не установлен")

# Логируем успешную загрузку (без показа самих ключей)
logger.info("✅ TELEGRAM_BOT_TOKEN загружен успешно")
logger.info("✅ NEUROAPI_KEY загружен успешно")
logger.info(f"🌐 NeuroAPI URL: {NEUROAPI_BASE_URL}")

# Безопасная проверка ключа (только для отладки)
if TELEGRAM_TOKEN:
    logger.info(f"📝 Длина TELEGRAM_TOKEN: {len(TELEGRAM_TOKEN)} символов")
if NEUROAPI_KEY:
    logger.info(f"📝 Длина NEUROAPI_KEY: {len(NEUROAPI_KEY)} символов")