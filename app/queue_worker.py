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
        # Here you would implement your message processing logic
        # For example, calling WhatsApp API to send response
        whatsapp_api_url = os.getenv('WHATSAPP_API_URL')
        api_token = os.getenv('WHATSAPP_API_TOKEN')
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        response_data = {
            "messaging_product": "whatsapp",
            "to": message_data['from_number'],
            "type": "text",
            "text": {"body": message_data['response_text']}
        }
        
        response = requests.post(whatsapp_api_url, json=response_data, headers=headers)
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
