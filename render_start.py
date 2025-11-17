import os
import threading
from bot import main as bot_main

def start_bot():
    """Запускает бота в отдельном потоке"""
    print("🤖 Starting Telegram bot...")
    bot_main()

if __name__ == '__main__':
    # Запускаем бота
    start_bot()