"""Lead processing service - orchestrates the lead automation flow."""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.core.exceptions import LeadNotFoundError, MetaAPIError, MondayAPIError
from src.core.logging import get_logger
from src.db.models import Lead
from src.services.meta import meta_service
from src.services.monday import (
    STATUS_MESSAGE_SENT,
    STATUS_NO_ANSWER_1,
    monday_service,
)

logger = get_logger(__name__)
settings = get_settings()

# Template names are configured in settings
# These must match approved templates in Meta Business


class LeadService:
    """Service for processing leads through the automation flow."""

    async def process_new_lead(
        self,
        session: AsyncSession,
        monday_item_id: str,
        phone_column_id: str | None = None,
        status_column_id: str | None = None,
    ) -> Lead:
        """
        Process a new lead from Monday.com webhook.

        1. Fetch lead details from Monday
        2. Store in database
        3. Send welcome WhatsApp message
        4. Update Monday status to "נשלחה הודעה"
        """
        # Use config values if not provided
        phone_column_id = phone_column_id or settings.monday_phone_column_id
        status_column_id = status_column_id or settings.monday_status_column_id
        
        logger.info(
            "processing_new_lead", 
            monday_item_id=monday_item_id,
            phone_column_id=phone_column_id,
        )

        # Check if lead already exists
        existing = await session.execute(
            select(Lead).where(Lead.monday_item_id == monday_item_id)
        )
        if existing.scalar_one_or_none():
            logger.warning("lead_already_exists", monday_item_id=monday_item_id)
            raise ValueError(f"Lead {monday_item_id} already processed")

        # Fetch lead details from Monday
        try:
            phone = await monday_service.get_phone_number_from_item(
                monday_item_id, phone_column_id
            )
            name = await monday_service.get_lead_name_from_item(monday_item_id)
        except MondayAPIError as e:
            logger.error("failed_to_fetch_lead", error=str(e))
            raise

        if not phone:
            logger.error("no_phone_number", monday_item_id=monday_item_id)
            raise ValueError(f"No phone number found for item {monday_item_id}")

        # Create lead in database
        now = datetime.utcnow()
        lead = Lead(
            monday_item_id=monday_item_id,
            phone_number=phone,
            lead_name=name or "Unknown",
            created_at=now,
            status=STATUS_MESSAGE_SENT,
            followup_due_at=now + timedelta(hours=24),
            is_done=False,
        )
        session.add(lead)

        # Send WhatsApp welcome message using template
        try:
            # Build template components with name parameter
            components = []
            if name:
                components = [
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": name}],
                    }
                ]
            
            await meta_service.send_template_message(
                phone,
                template_name=settings.whatsapp_welcome_template,
                language_code=settings.whatsapp_template_language,
                components=components if components else None,
            )
        except MetaAPIError as e:
            logger.error("failed_to_send_whatsapp", error=str(e))
            # Still save the lead but don't update Monday status
            raise

        # Update Monday status
        try:
            await monday_service.update_item_status(
                monday_item_id, STATUS_MESSAGE_SENT, status_column_id
            )
        except MondayAPIError as e:
            logger.error("failed_to_update_monday_status", error=str(e))
            # Message was sent, so continue despite Monday update failure

        logger.info("lead_processed_successfully", lead_id=lead.id, phone=phone)
        return lead

    async def process_followup(
        self,
        session: AsyncSession,
        lead: Lead,
        status_column_id: str = "status",
    ) -> bool:
        """
        Process 24h follow-up for a lead.

        1. Safety Check: Query Monday for current status
        2. If status is "נשלחה הודעה" -> Send follow-up
        3. Update Monday status to "אין מענה 1"

        Returns True if follow-up was sent, False if aborted.
        """
        logger.info("processing_followup", lead_id=lead.id)

        # Safety Check: Query Monday for current status
        try:
            current_status = await monday_service.get_item_status(
                lead.monday_item_id, status_column_id
            )
        except MondayAPIError as e:
            logger.error("safety_check_failed", error=str(e))
            raise

        # Abort if status changed (human intervention occurred)
        if current_status != STATUS_MESSAGE_SENT:
            logger.info(
                "followup_aborted_status_changed",
                lead_id=lead.id,
                current_status=current_status,
            )
            lead.is_done = True
            return False

        # Send follow-up message using template
        try:
            components = []
            if lead.lead_name:
                components = [
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": lead.lead_name}],
                    }
                ]
            
            await meta_service.send_template_message(
                lead.phone_number,
                template_name=settings.whatsapp_followup_template,
                language_code=settings.whatsapp_template_language,
                components=components if components else None,
            )
        except MetaAPIError as e:
            logger.error("failed_to_send_followup", error=str(e))
            raise

        # Update Monday status to "אין מענה 1"
        try:
            await monday_service.update_item_status(
                lead.monday_item_id, STATUS_NO_ANSWER_1, status_column_id
            )
        except MondayAPIError as e:
            logger.error("failed_to_update_monday_followup", error=str(e))
            # Continue - message was sent

        # Update lead status in DB
        lead.status = STATUS_NO_ANSWER_1
        lead.is_done = True

        logger.info("followup_sent_successfully", lead_id=lead.id)
        return True

    async def mark_lead_replied(
        self,
        session: AsyncSession,
        phone_number: str,
    ) -> Lead | None:
        """
        Mark a lead as having replied (for incoming message handling).

        Returns the lead if found and updated, None otherwise.
        """
        # Normalize phone number for lookup
        # Meta sends without +, we store with +, so try both formats
        normalized = phone_number.lstrip("+")
        phone_with_plus = f"+{normalized}"

        result = await session.execute(
            select(Lead).where(
                Lead.phone_number.in_([normalized, phone_with_plus, phone_number]),
                Lead.is_done == False,  # noqa: E712
            )
        )
        lead = result.scalar_one_or_none()

        if lead:
            lead.is_done = True
            logger.info("lead_marked_replied", lead_id=lead.id, phone=phone_number)
            return lead

        logger.warning("no_active_lead_for_reply", phone=phone_number)
        return None

    async def get_leads_pending_followup(
        self, session: AsyncSession
    ) -> list[Lead]:
        """Get all leads that are due for follow-up."""
        now = datetime.utcnow()
        result = await session.execute(
            select(Lead).where(
                Lead.is_done == False,  # noqa: E712
                Lead.followup_due_at <= now,
            )
        )
        return list(result.scalars().all())


lead_service = LeadService()
