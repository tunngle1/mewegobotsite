import os
import json
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["https://mewegrowth.vercel.app", "http://localhost:*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"]
    }
})

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_FILE = '../admin_chat_id.json'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def send_telegram_message(text: str, chat_id: str = None) -> bool:
    """Отправка сообщения через Telegram API"""
    target_chat_id = chat_id or load_admin_chat_id()
    
    if not target_chat_id:
        logger.error("Не установлен CHAT_ID для отправки сообщений")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": target_chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info(f"Сообщение успешно отправлено в чат {target_chat_id}")
            return True
        else:
            logger.error(f"Ошибка Telegram API: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Ошибка при отправке в Telegram: {e}")
        return False

@app.route('/', methods=['POST', 'OPTIONS'])
def handle_xray():
    """Обработка результатов Business X-Ray"""
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
    
    try:
        logger.info(f"Получен X-Ray результат: {request.json}")
        data = request.json
        
        message = f"""
🔍 <b>РЕЗУЛЬТАТ BUSINESS X-RAY</b>

👤 <b>Имя:</b> {data.get('name', 'Не указано')}
🏢 <b>Компания:</b> {data.get('company', 'Не указано')}

📊 <b>Результаты опроса:</b>
{data.get('results', 'Нет результатов')}

⏰ <b>Время:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        success = send_telegram_message(message)
        
        if success:
            return jsonify({"status": "success", "message": "Результаты отправлены"})
        else:
            return jsonify({"status": "error", "message": "Ошибка при отправке - бот не добавлен в чат"}), 500
            
    except Exception as e:
        logger.error(f"Ошибка при обработке X-Ray: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500