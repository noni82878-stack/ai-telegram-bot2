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
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовые сообщения с помощью ИИ"""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"Сообщение от {user_id}: {user_message}")
    
    # Показываем что бот печатает
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Получаем историю диалога
        conversation_history = get_user_history(user_id)
        
        # Генерируем ответ через ИИ
        ai_response = ai_handler.generate_response(user_message, conversation_history)
        
        # Сохраняем в историю
        add_to_history(user_id, user_message, ai_response)
        
        # Отправляем ответ
        await update.message.reply_text(ai_response)
        
    except Exception as e:
        logger.error(f"Ошибка в handle_message: {e}")
        await update.message.reply_text("Упс, что-то пошло не так... Давай попробуем еще раз? 😅")

# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Логирует ошибки"""
    logger.error(f"Ошибка: {context.error}")

def main():
    """Запускает бота"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("🤖 Бот запускается с ИИ...")
    application.run_polling()
    print("✅ Бот с ИИ работает!")

if __name__ == '__main__':
    main()