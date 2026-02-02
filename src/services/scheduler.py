"""APScheduler service for background job processing."""

from datetime import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.core.config import get_settings
from src.core.logging import get_logger
from src.db.session import get_session
from src.services.lead import lead_service

logger = get_logger(__name__)
settings = get_settings()

# Israel timezone for time window checks
ISRAEL_TZ = pytz.timezone("Asia/Jerusalem")


class SchedulerService:
    """Background scheduler for processing initial messages and follow-ups."""

    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self._is_running = False

    def is_within_send_window(self) -> bool:
        """
        Check if current time is within allowed send window (08:00 - 21:00 Israel Time).
        """
        now_israel = datetime.now(ISRAEL_TZ)
        current_hour = now_israel.hour
        return settings.send_window_start_hour <= current_hour < settings.send_window_end_hour

    async def process_pending_initial_messages(self) -> None:
        """
        Process all leads that are due for initial message sending.

        This job runs frequently (every 1-2 minutes) and:
        1. Checks if within send window
        2. Fetches leads with first_message_due_at <= now and first_message_sent = False
        3. Sends the initial welcome message for each lead
        """
        logger.info("initial_message_job_started")

        # Check time window
        if not self.is_within_send_window():
            logger.info(
                "outside_send_window_initial",
                current_hour=datetime.now(ISRAEL_TZ).hour,
            )
            return

        async with get_session() as session:
            try:
                leads = await lead_service.get_leads_pending_initial_message(session)
                logger.info("pending_initial_messages_found", count=len(leads))

                for lead in leads:
                    try:
                        await lead_service.send_initial_message(session, lead)
                    except Exception as e:
                        logger.error(
                            "initial_message_error",
                            lead_id=lead.id,
                            error=str(e),
                        )
                        # Continue processing other leads

            except Exception as e:
                logger.error("initial_message_job_error", error=str(e))

        logger.info("initial_message_job_completed")

    async def process_pending_followups(self) -> None:
        """
        Process all leads that are due for follow-up.

        This job runs frequently and:
        1. Checks if within send window
        2. Fetches leads with followup_due_at < now and is_done = False
        3. For each lead, runs Safety Check and sends follow-up if appropriate
        """
        logger.info("followup_job_started")

        # Check time window
        if not self.is_within_send_window():
            logger.info(
                "outside_send_window_followup",
                current_hour=datetime.now(ISRAEL_TZ).hour,
            )
            return

        async with get_session() as session:
            try:
                leads = await lead_service.get_leads_pending_followup(session)
                logger.info("pending_followups_found", count=len(leads))

                for lead in leads:
                    try:
                        await lead_service.process_followup(session, lead)
                    except Exception as e:
                        logger.error(
                            "followup_processing_error",
                            lead_id=lead.id,
                            error=str(e),
                        )
                        # Continue processing other leads

            except Exception as e:
                logger.error("followup_job_error", error=str(e))

        logger.info("followup_job_completed")

    def start(self) -> None:
        """Start the scheduler with message processing jobs."""
        if self._is_running:
            logger.warning("scheduler_already_running")
            return

        interval_minutes = settings.scheduler_interval_minutes

        # Add job for initial message processing (runs every 1-2 minutes)
        self.scheduler.add_job(
            self.process_pending_initial_messages,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id="process_initial_messages",
            name="Process pending initial messages",
            replace_existing=True,
        )

        # Add job for follow-up processing (runs every 1-2 minutes)
        self.scheduler.add_job(
            self.process_pending_followups,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id="process_followups",
            name="Process pending follow-ups",
            replace_existing=True,
        )

        self.scheduler.start()
        self._is_running = True
        logger.info(
            "scheduler_started",
            interval_minutes=interval_minutes,
            initial_message_delay=settings.initial_message_delay_minutes,
        )

    def stop(self) -> None:
        """Stop the scheduler."""
        if not self._is_running:
            return

        self.scheduler.shutdown(wait=False)
        self._is_running = False
        logger.info("scheduler_stopped")


scheduler_service = SchedulerService()
