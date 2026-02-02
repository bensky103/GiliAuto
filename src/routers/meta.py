"""Meta WhatsApp webhook router."""

from fastapi import APIRouter, Query, Request
from fastapi.responses import PlainTextResponse, JSONResponse

from src.core.config import get_settings
from src.core.logging import get_logger
from src.db.session import get_session
from src.services.lead import lead_service
from src.services.monday import STATUS_CUSTOMER_REPLIED, monday_service

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/webhook", tags=["webhooks"])


@router.get("/meta")
async def meta_webhook_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
) -> PlainTextResponse:
    """
    Handle Meta webhook verification.

    Meta sends a GET request with hub.mode, hub.verify_token, and hub.challenge
    to verify the webhook endpoint.
    """
    logger.info(
        "meta_webhook_verification",
        mode=hub_mode,
        token_present=bool(hub_verify_token),
    )

    if hub_mode == "subscribe" and hub_verify_token == settings.admin_secret:
        logger.info("meta_webhook_verified")
        return PlainTextResponse(content=hub_challenge or "")

    logger.warning("meta_webhook_verification_failed")
    return PlainTextResponse(content="Verification failed", status_code=403)


@router.post("/meta")
async def meta_webhook(request: Request) -> JSONResponse:
    """
    Handle incoming WhatsApp messages from Meta.

    When a lead replies:
    1. Find the lead in DB by phone number
    2. Mark as done
    3. Update Monday status to indicate reply received

    Always returns 200 to acknowledge receipt.
    """
    try:
        body = await request.json()
        logger.info("meta_webhook_received", body=body)

        # Navigate to messages in the webhook payload
        entries = body.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])

                for message in messages:
                    sender_phone = message.get("from")
                    message_type = message.get("type")
                    message_id = message.get("id")

                    logger.info(
                        "incoming_whatsapp_message",
                        from_phone=sender_phone,
                        type=message_type,
                        message_id=message_id,
                    )

                    if not sender_phone:
                        continue

                    # Process the incoming message
                    async with get_session() as session:
                        lead = await lead_service.mark_lead_replied(
                            session, sender_phone
                        )

                        if lead:
                            # Update Monday status to indicate customer replied
                            try:
                                await monday_service.update_item_status(
                                    lead.monday_item_id,
                                    STATUS_CUSTOMER_REPLIED,
                                )
                                logger.info(
                                    "monday_status_updated_on_reply",
                                    lead_id=lead.id,
                                )
                            except Exception as e:
                                logger.error(
                                    "failed_to_update_monday_on_reply",
                                    error=str(e),
                                )

        return JSONResponse(content={"status": "received"})

    except Exception as e:
        logger.error("meta_webhook_error", error=str(e))
        # Always return 200 to acknowledge
        return JSONResponse(content={"status": "error"})
