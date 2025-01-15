# WhatsApp Chatbot

A robust WhatsApp chatbot implementation with SQLite database integration and message queue processing.

## Features

- FastAPI-based webhook endpoint for WhatsApp API integration
- Async SQLite database using SQLAlchemy
- Message queue system using Redis and RQ for handling high message volumes
- Webhook verification and logging
- Error handling and monitoring
- Asynchronous message processing

## Requirements

- Python 3.8+
- Redis server
- Virtual environment

## Installation

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start Redis server (if not already running):
```bash
redis-server
```

5. Start the worker process:
```bash
python -c "from app.queue_worker import start_worker; start_worker()"
```

6. Run the application:
```bash
uvicorn app.main:app --reload
```

## Docker Installation

1. Make sure you have Docker and Docker Compose installed on your server.

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Build and start the containers:
```bash
docker-compose up -d --build
```

This will start three containers:
- API server (FastAPI application)
- Worker (Message queue processor)
- Redis (Message queue backend)

4. Check the logs:
```bash
# All containers
docker-compose logs -f

# Specific container
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f redis
```

5. Stop the containers:
```bash
docker-compose down
```

## Data Persistence

The application uses two types of persistent storage:
- SQLite database is stored in the `./data` directory
- Redis data is stored in a named volume `redis_data`

Both will persist across container restarts.

## API Endpoints

- `POST /webhook`: Handles incoming WhatsApp messages and webhooks
- `GET /messages`: Retrieves message history

### Webhook Configuration

The application provides two webhook endpoints for WhatsApp integration:

- `GET /webhook`: Used for webhook verification
- `POST /webhook`: Handles incoming WhatsApp messages

#### Setting up WhatsApp Webhook

1. Deploy the application to your server using Docker
2. Configure your environment variables in `.env`:
```bash
WHATSAPP_API_URL=your_whatsapp_api_url
WHATSAPP_API_TOKEN=your_whatsapp_api_token
WEBHOOK_VERIFY_TOKEN=your_verification_token  # Example: alvaroenrique
```

3. In the WhatsApp Business API/Cloud API dashboard:
   - Callback URL: `https://your-domain.com/webhook`
   - Verify token: Enter the same token you set in `WEBHOOK_VERIFY_TOKEN`
   - Click "Verify and Save"

The system will automatically:
- Verify your webhook endpoint
- Start receiving messages at the POST endpoint
- Process messages through the queue system
- Store messages in the SQLite database

#### Webhook Security

- Always use HTTPS for your webhook URL
- Use a strong verification token
- All webhook calls are logged in the database for audit purposes

## Database Schema

### Messages Table
- id: Primary key
- whatsapp_message_id: Unique message ID from WhatsApp
- from_number: Sender's phone number
- message_text: Content of the message
- timestamp: Message receipt time
- status: Message processing status
- response_text: Bot's response

### WebhookLog Table
- id: Primary key
- webhook_type: Type of webhook event
- payload: Raw webhook data
- timestamp: Event time
- status: Processing status
- error_message: Error details if any

## Best Practices Implemented

1. **Asynchronous Processing**
   - Uses FastAPI for async request handling
   - Implements async database operations
   - Message queue for handling high volumes

2. **Data Persistence**
   - SQLite database with SQLAlchemy ORM
   - Proper schema design and indexing
   - Async database operations

3. **Error Handling**
   - Comprehensive error logging
   - Webhook verification
   - Exception handling

4. **Security**
   - Environment variables for sensitive data
   - Webhook verification token
   - API token management

5. **Scalability**
   - Message queue implementation
   - Async processing
   - Connection pooling

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
