import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN
from ai_handler import AIHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализируем ИИ-обработчик
ai_handler = AIHandler()

# Для хранения истории диалогов (временное решение)
user_conversations = {}

def get_user_history(user_id: int) -> list:
    """Получает историю диалога для пользователя"""
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    return user_conversations[user_id]

def add_to_history(user_id: int, user_message: str, ai_response: str):
    """Добавляет сообщение в историю диалога"""
    history = get_user_history(user_id)
    
    # Добавляем сообщение пользователя и ответ ИИ
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": ai_response})
    
    # Ограничиваем историю последними 10 сообщениями
    if len(history) > 10:
        user_conversations[user_id] = history[-10:]

# Обработчик команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
👋 Привет! Я Аня - твой ИИ-собеседник.

Давай пообщаемся! Расскажи мне что-нибудь о себе, или просто поздоровайся 😊

Не стесняйся писать обо всем - я люблю новые знакомства!
"""
    await update.message.reply_text(welcome_text)

# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🤖 Помощь по боту:

Просто напиши мне сообщение, и я отвечу!

Команды:
/start - начать общение
/help - эта справка
/clear - очистить историю нашего диалога

Пиши naturally, как в обычном чате!
"""
    await update.message.reply_text(help_text)

# Обработчик команды /clear
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очищает историю диалога"""
    user_id = update.effective_user.id
    if user_id in user_conversations:
        user_conversations[user_id] = []
    await update.message.reply_text("💫 Наша история диалога очищена! Давай начнем заново!")

# Обработчик текстовых сообщений
aasync def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовые сообщения и медиа с подписями"""
    # Получаем текст сообщения или подпись к медиа
    user_message = update.message.text or update.message.caption
    
    # Если сообщение пустое (нет текста и нет подписи)
    if not user_message:
        await update.message.reply_text(
            "Привет! Я понимаю только текстовые сообщения 😊\n"
            "Напиши мне что-нибудь, и я с радостью отвечу!"
        )
        return
    
    user_id = update.effective_user.id
    
    logger.info(f"📨 Сообщение от {user_id}: {user_message}")
    
    # Показываем что бот печатает
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Генерируем ответ с учетом пользователя
        ai_response = ai_handler.generate_response(user_id, user_message)
        await update.message.reply_text(ai_response)
        
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_message: {e}")
        await update.message.reply_text("Упс, что-то пошло не так... Давай попробуем еще раз? 😅")

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает медиафайлы без текстовых подписей"""
    media_responses = [
        "Классное фото! 📸 Расскажи, что на нем?",
        "Интересно! А что это? 😊",
        "Красиво! Хочешь рассказать об этом?",
        "Ух ты! А что здесь происходит? 🤔",
        "Интересное изображение! О чём оно? 😄"
    ]
    
    import random
    response = random.choice(media_responses)
    await update.message.reply_text(response)
    
# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Логирует ошибки"""
    logger.error(f"Ошибка: {context.error}")
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", start_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("clear", clear_command))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработчик медиафайлов (фото, видео, документы) без подписей
    application.add_handler(MessageHandler(
        (filters.PHOTO | filters.VIDEO | filters.DOCUMENT) & ~filters.COMMAND, 
        handle_media
    ))
    
    # Обработчик для всего остального (стикеры, голосовые и т.д.)
    application.add_handler(MessageHandler(
        ~filters.TEXT & ~filters.COMMAND & ~filters.PHOTO & ~filters.VIDEO & ~filters.DOCUMENT,
        handle_media
    ))
    
    print("🤖 Бот запускается...")
    application.run_polling()
    print("✅ Бот работает!")