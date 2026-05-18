from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.whatsapp_bot_service import WhatsAppBotService
from app.core.logger import request_logger
from app.core.config import settings

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Bot"])


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """Verify Meta Webhook."""
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        return PlainTextResponse(content=hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def handle_whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle incoming messages from waofficial."""
    data = await request.json()
    request_logger.info(f"WA webhook payload: {data}")

    try:
        # waofficial wraps payload: {"event": "message", "data": {...}}
        if data.get("event") == "message":
            inner = data.get("data", {})
            mobile = inner.get("senderPhoneNumber")
            phone_id = inner.get("recipientPhoneNumberId")
            msg_type = inner.get("messageType", "text")
            content = inner.get("content", {})
            text = content.get("text", "")
            # interactive reply
            if not text and msg_type == "interactive":
                text = content.get("id") or content.get("title", "")
        else:
            # fallback for direct test posts
            mobile = data.get("from")
            phone_id = data.get("phoneNoId")
            msg_type = data.get("type", "text")
            text_obj = data.get("text", "")
            text = text_obj if isinstance(text_obj, str) else text_obj.get("body", "")

        if not mobile or not text:
            request_logger.info(f"WA webhook ignored: type={msg_type} mobile={mobile} text={text!r}")
            return {"status": "ignored"}

        from app.models.tenant import Tenant
        tenant = db.query(Tenant).filter(Tenant.whatsapp_phone_id == phone_id).first()

        if not tenant:
            request_logger.warning(f"No tenant for phone_id={phone_id}, trying all tenants with WA configured")
            tenant = db.query(Tenant).filter(Tenant.whatsapp_phone_id.isnot(None)).first()

        if not tenant:
            request_logger.warning(f"No tenant found for phone_number_id={phone_id}")
            return {"status": "ignored"}

        tenant_id = tenant.tenant_id

        # 3. Process via Bot Service
        bot = WhatsAppBotService(db, tenant_id)
        await bot.handle_incoming(mobile, text)
        
        return {"status": "success"}
        
    except Exception as e:
        request_logger.error(f"WhatsApp Webhook Error: {str(e)}")
        # Meta expects 200 even on error to stop retries, but we'll log it
        return {"status": "error", "detail": str(e)}

@router.post("/test-incoming")
async def test_incoming_message(
    mobile: str, 
    text: str, 
    tenant_id: str = "test_tenant_bulk",
    db: Session = Depends(get_db)
):
    """Simulate an incoming WhatsApp message for testing."""
    bot = WhatsAppBotService(db, tenant_id)
    await bot.handle_incoming(mobile, text)
    return {"status": "simulated"}
