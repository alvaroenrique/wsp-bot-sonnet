import redis
from rq import Queue, Worker, Connection
import os
import requests
from datetime import datetime

# Redis connection
redis_conn = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0
)

# Create queue
message_queue = Queue('whatsapp_messages', connection=redis_conn)

def process_message(message_data):
    """
    Process message in background
    """
    try:
        whatsapp_api_url = os.getenv('WHATSAPP_API_URL')
        api_token = os.getenv('WHATSAPP_API_TOKEN')
        phone_id = os.getenv('WHATSAPP_PHONE_ID')
        
        if not all([whatsapp_api_url, api_token, phone_id]):
            raise ValueError("Missing required WhatsApp configuration")
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        # Construct the complete WhatsApp API URL with phone ID
        complete_api_url = f"{whatsapp_api_url}/{phone_id}/messages"
        
        response_data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": message_data['from_number'],
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message_data.get('response_text', os.getenv('DEFAULT_RESPONSE_MESSAGE', 'Gracias por tu mensaje'))
            }
        }
        
        response = requests.post(complete_api_url, json=response_data, headers=headers)
        response.raise_for_status()
        
        return {
            'status': 'success',
            'message_id': message_data['whatsapp_message_id'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message_id': message_data['whatsapp_message_id'],
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

def start_worker():
    """
    Start the RQ worker
    """
    with Connection(redis_conn):
        worker = Worker([message_queue])
        worker.work()
