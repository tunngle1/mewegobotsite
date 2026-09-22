from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_FILE = 'admin_chat_id.json'

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех запросов
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

@app.route('/webhook/lead', methods=['POST', 'OPTIONS'])
def handle_lead():
    """Обработка заявки с формы сайта"""
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.json
        
        # Формирование сообщения
        message = f"""
📝 <b>НОВАЯ ЗАЯВКА С САЙТА</b>

👤 <b>Имя:</b> {data.get('name', 'Не указано')}
🏢 <b>Компания:</b> {data.get('company', 'Не указано')}
📊 <b>Оборот:</b> {data.get('turnover', 'Не указано')}
👥 <b>Размер команды:</b> {data.get('team', 'Не указано')}
📈 <b>Выручка:</b> {data.get('revenue', 'Не указано')}
💬 <b>Контакт:</b> {data.get('contact', 'Не указано')} ({data.get('contact_type', 'Не указано')})
🌐 <b>Сайт:</b> {data.get('site', 'Не указано')}

📝 <b>Что происходит:</b>
{data.get('what', 'Не указано')}

🎯 <b>Ситуация:</b> {data.get('problem', 'Не выбрана')}

⏰ <b>Время:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        success = send_telegram_message(message)
        
        if success:
            return jsonify({"status": "success", "message": "Заявка отправлена"})
        else:
            return jsonify({"status": "error", "message": "Ошибка при отправке - бот не добавлен в чат"}), 500
            
    except Exception as e:
        logger.error(f"Ошибка при обработке заявки: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook/xray', methods=['POST'])
def handle_xray():
    """Обработка результатов Business X-Ray"""
    try:
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

@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья сервиса"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)