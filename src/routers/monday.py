"""Monday.com webhook router."""

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src.core.logging import get_logger
from src.db.session import get_session
from src.schemas.monday import MondayWebhookPayload
from src.services.lead import lead_service

logger = get_logger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhooks"])


@router.post("/monday")
async def monday_webhook(request: Request) -> JSONResponse:
    """
    Handle Monday.com webhook events.

    Handles:
    - Challenge verification (for webhook setup)
    - New item creation events

    Always returns 200 to prevent retries per STANDARDS.md.
    """
    try:
        body = await request.json()
        logger.info("monday_webhook_received", body=body)

        # Handle challenge verification
        if "challenge" in body:
            logger.info("monday_challenge_received")
            return JSONResponse(content={"challenge": body["challenge"]})

        # Parse webhook payload
        try:
            payload = MondayWebhookPayload(**body)
        except Exception as e:
            logger.error("invalid_webhook_payload", error=str(e))
            return JSONResponse(content={"status": "invalid payload"}, status_code=200)

        event = payload.event
        item_id = str(event.pulseId)

        logger.info(
            "processing_monday_event",
            item_id=item_id,
            board_id=event.boardId,
            group_id=event.groupId,
        )

        # Process the new lead
        async with get_session() as session:
            try:
                await lead_service.process_new_lead(session, item_id)
                return JSONResponse(content={"status": "processed"})
            except ValueError as e:
                # Lead already exists or missing data
                logger.warning("lead_processing_skipped", error=str(e))
                return JSONResponse(content={"status": "skipped", "reason": str(e)})
            except Exception as e:
                logger.error("lead_processing_failed", error=str(e))
                # Return 200 to prevent retries
                return JSONResponse(content={"status": "error", "reason": str(e)})

    except Exception as e:
        logger.error("webhook_handler_error", error=str(e))
        # Always return 200 to prevent retries
        return JSONResponse(content={"status": "error"})
