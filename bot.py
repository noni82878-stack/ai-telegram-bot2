import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes
from config import TELEGRAM_TOKEN
from ai_handler import AIHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ai_handler = AIHandler()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """
👋 Привет! Я Аня - твой ИИ-собеседник.

Давай познакомимся поближе! Я люблю:
🎨 Искусство и фотографию
🎵 Музыку (играю на гитаре)
✈️ Путешествия
📚 Интересные беседы

Просто напиши мне что-нибудь, и я с радостью отвечу!

Команды:
/start - это сообщение
/help - помощь
/clear - очистить историю нашего разговора
/about - обо мне
"""
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text("Просто напиши мне сообщение, и я отвечу! 😊")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /about"""
    about_text = """
ℹ️ Обо мне:

Я - Аня, ИИ-собеседник с характером и увлечениями. 
Мне 25 лет, я из Санкт-Петербурга.

Мои интересы:
• Живопись и современное искусство
• Игра на гитаре (люблю инди-рок)
• Путешествия (была в 15 странах)
• Фотография и кулинария

Я помню наши разговоры и стараюсь быть интересным собеседником!
"""
    await update.message.reply_text(about_text)

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /clear - очищает историю диалога"""
    user_id = update.effective_user.id
    ai_handler.memory_manager.clear_history(user_id)
    await update.message.reply_text("💫 Наша история диалога очищена! Начнем заново!")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ТОЛЬКО текстовые сообщения"""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    if not user_message or not user_message.strip():
        await update.message.reply_text("Привет! Напиши что-нибудь текстом 😊")
        return
    
    logger.info(f"📨 Текст от {user_id}: {user_message}")
    
    # Показываем что бот печатает
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Генерируем ответ
        ai_response = ai_handler.generate_response(user_id, user_message)
        await update.message.reply_text(ai_response)
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_text_message: {e}")
        await update.message.reply_text("Упс, что-то пошло не так... Давай попробуем еще раз? 😅")

async def handle_media_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает медиафайлы (фото, видео, документы)"""
    media_responses = [
        "Интересно! 📸 Но я лучше понимаю текстовые сообщения 😊",
        "Классно! 🖼️ Напиши мне что-нибудь об этом текстом?",
        "Ух ты! ✨ А теперь расскажи об этом словами?",
        "Красиво! 🌟 Хочешь поделиться историей текстом?"
    ]
    
    import random
    response = random.choice(media_responses)
    await update.message.reply_text(response)

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает все остальные типы сообщений (стикеры, голосовые и т.д.)"""
    other_responses = [
        "Привет! Я понимаю только текстовые сообщения и фото 😊",
        "Ой, я пока не умею работать с такими сообщениями... Напиши мне текст! 💫",
        "Интересно! Но я лучше понимаю текстовые сообщения 😅"
    ]
    
    import random
    response = random.choice(other_responses)
    await update.message.reply_text(response)

def main():
    """Запускает бота"""
    from telegram.ext import filters
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("clear", clear_command))
    
    # Обработчик для текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Обработчик для медиафайлов (фото, видео, документы)
    application.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.ATTACHMENT, 
        handle_media_message
    ))
    
    # Обработчик для всего остального
    application.add_handler(MessageHandler(
        ~filters.TEXT & ~filters.COMMAND & ~filters.PHOTO & ~filters.VIDEO & ~filters.ATTACHMENT,
        handle_other_messages
    ))
    
    print("🤖 Бот запускается...")
    application.run_polling()
    print("✅ Бот работает!")

if __name__ == '__main__':
    main()