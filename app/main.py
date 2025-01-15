from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models, schemas
from .database import engine, get_db
from .queue_worker import message_queue
import json
from datetime import datetime
import os
from sqlalchemy import select

app = FastAPI(title="WhatsApp Chatbot API")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Handle WhatsApp webhook verification
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == os.getenv("WEBHOOK_VERIFY_TOKEN"):
            if challenge:
                return int(challenge)
            return "OK"
        raise HTTPException(status_code=403, detail="Verification token mismatch")
    
    raise HTTPException(status_code=400, detail="Invalid verification request")

@app.post("/webhook")
async def webhook_handler(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handle incoming webhooks from WhatsApp
    """
    try:
        body = await request.json()
        
        # Log webhook
        webhook_log = models.WebhookLog(
            webhook_type="message",
            payload=json.dumps(body),
            status="received"
        )
        db.add(webhook_log)
        await db.commit()

        # Process messages
        if "entry" in body and body["entry"]:
            for entry in body["entry"]:
                if "changes" in entry and entry["changes"]:
                    for change in entry["changes"]:
                        if change.get("value", {}).get("messages"):
                            for msg in change["value"]["messages"]:
                                # Create message record
                                message = models.Message(
                                    whatsapp_message_id=msg["id"],
                                    from_number=msg["from"],
                                    message_text=msg.get("text", {}).get("body", ""),
                                    timestamp=datetime.utcnow()
                                )
                                db.add(message)
                                await db.commit()

                                # Queue message for processing
                                message_queue.enqueue(
                                    'app.queue_worker.process_message',
                                    {
                                        'whatsapp_message_id': msg["id"],
                                        'from_number': msg["from"],
                                        'message_text': msg.get("text", {}).get("body", ""),
                                        'response_text': "Thank you for your message! We'll process it shortly."
                                    }
                                )

        return {"status": "success"}

    except Exception as e:
        # Log error
        webhook_log = models.WebhookLog(
            webhook_type="error",
            payload=str(e),
            status="error",
            error_message=str(e)
        )
        db.add(webhook_log)
        await db.commit()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/messages")
async def get_messages(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Get list of messages
    """
    query = select(models.Message).offset(skip).limit(limit)
    result = await db.execute(query)
    messages = result.scalars().all()
    return [schemas.Message.model_validate(message) for message in messages]
