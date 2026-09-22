import os
import json
import logging
import requests
from datetime import datetime

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

def handler(request):
    """Vercel serverless function handler"""
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Accept',
        'Access-Control-Allow-Methods': 'POST,OPTIONS,GET',
        'Content-Type': 'application/json'
    }
    
    # Handle OPTIONS request
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'status': 'ok'})
        }
    
    # Handle GET request (for testing)
    if request.method == 'GET':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'xray endpoint working',
                'message': 'Use POST for form submissions'
            })
        }
    
    # Handle POST request
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            logger.info(f"Получен X-Ray результат: {body}")
            
            message = f"""
🔍 <b>РЕЗУЛЬТАТ BUSINESS X-RAY</b>

👤 <b>Имя:</b> {body.get('name', 'Не указано')}
🏢 <b>Компания:</b> {body.get('company', 'Не указано')}

📊 <b>Результаты опроса:</b>
{body.get('results', 'Нет результатов')}

⏰ <b>Время:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            success = send_telegram_message(message)
            
            if success:
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({'status': 'success', 'message': 'Результаты отправлены'})
                }
            else:
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({'status': 'error', 'message': 'Ошибка при отправке - бот не добавлен в чат'})
                }
                
        except Exception as e:
            logger.error(f"Ошибка при обработке X-Ray: {e}")
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'status': 'error', 'message': str(e)})
            }
    
    return {
        'statusCode': 405,
        'headers': headers,
        'body': json.dumps({'status': 'error', 'message': 'Method not allowed'})
    }