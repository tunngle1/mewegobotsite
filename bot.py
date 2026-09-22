import os
import logging
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_FILE = 'admin_chat_id.json'

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def save_admin_chat_id(chat_id: str) -> None:
    """Сохранение chat_id администратора в файл"""
    try:
        with open(ADMIN_CHAT_FILE, 'w') as f:
            json.dump({'chat_id': chat_id}, f)
        logger.info(f"Chat ID {chat_id} сохранён как администратор")
    except Exception as e:
        logger.error(f"Ошибка при сохранении chat_id: {e}")

def load_admin_chat_id() -> str:
    """Загрузка chat_id администратора из файла"""
    try:
        if os.path.exists(ADMIN_CHAT_FILE):
            with open(ADMIN_CHAT_FILE, 'r') as f:
                data = json.load(f)
                return data.get('chat_id')
    except Exception as e:
        logger.error(f"Ошибка при загрузке chat_id: {e}")
    return None

async def start(update: Update, context: ContextTypes.DEFAULT) -> None:
    """Обработчик команды /start"""
    chat_id = str(update.effective_chat.id)
    
    # Сохраняем chat_id как администратора
    save_admin_chat_id(chat_id)
    
    await update.message.reply_text(
        '👋 Привет! Я бот для приёма заявок с сайта MeWeGo Growth.\n\n'
        '✅ Этот чат ' + chat_id + ' теперь настроен для получения заявок.\n\n'
        'Форма на сайте будет отправлять заявки сюда.\n\n'
        'Администратор: @melikhova_natalya'
    )

async def set_chat(update: Update, context: ContextTypes.DEFAULT) -> None:
    """Команда для установки chat_id администратора"""
    chat_id = str(update.effective_chat.id)
    save_admin_chat_id(chat_id)
    
    await update.message.reply_text(
        '✅ Chat ID ' + chat_id + ' сохранён как администратор.\n'
        'Теперь заявки с сайта будут приходить в этот чат.'
    )

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT) -> None:
    """Команда для получения текущего chat_id"""
    chat_id = str(update.effective_chat.id)
    await update.message.reply_text(
        '📱 Ваш Chat ID: ' + chat_id + '\n\n'
        'Используйте этот ID для настройки бота.'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT) -> None:
    """Обработчик текстовых сообщений"""
    if update.message.text:
        await update.message.reply_text(
            '💬 Получено сообщение:\n\n' + update.message.text + '\n\n'
            'Сообщение будет обработано администратором.'
        )

async def send_to_chat(text: str, application: Application) -> None:
    """Отправка сообщения в чат администратора"""
    chat_id = load_admin_chat_id()
    if not chat_id:
        logger.error("Не найден chat_id администратора")
        return
    
    try:
        await application.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode='HTML'
        )
        logger.info("Сообщение успешно отправлено в чат " + chat_id)
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")

def main() -> None:
    """Запуск бота"""
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setchat", set_chat))
    application.add_handler(CommandHandler("chatid", get_chat_id))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()