"""Meta WhatsApp Business API client service."""

from typing import Any

import httpx

from src.core.config import get_settings
from src.core.exceptions import MetaAPIError
from src.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

META_API_BASE_URL = "https://graph.facebook.com/v18.0"


class MetaService:
    """Service for interacting with Meta WhatsApp Business API."""

    def __init__(self) -> None:
        self.api_token = settings.meta_api_token
        self.phone_id = settings.meta_phone_id
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    async def send_text_message(self, to_phone: str, message: str) -> dict[str, Any]:
        """
        Send a text message via WhatsApp.

        Args:
            to_phone: Phone number in E.164 format (e.g., +972501234567)
            message: The text message to send

        Returns:
            The API response containing message ID
        """
        url = f"{META_API_BASE_URL}/{self.phone_id}/messages"

        # Normalize phone number (remove + if present, Meta expects without it)
        normalized_phone = to_phone.lstrip("+")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": normalized_phone,
            "type": "text",
            "text": {"body": message},
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                logger.info(
                    "whatsapp_message_sent",
                    to=normalized_phone,
                    message_id=data.get("messages", [{}])[0].get("id"),
                )
                return data
            except httpx.HTTPStatusError as e:
                error_data = e.response.json() if e.response.content else {}
                logger.error(
                    "meta_api_error",
                    status_code=e.response.status_code,
                    error=error_data,
                )
                raise MetaAPIError(f"Meta API error: {error_data}") from e
            except httpx.HTTPError as e:
                logger.error("meta_http_error", error=str(e))
                raise MetaAPIError(f"HTTP error communicating with Meta: {e}") from e

    async def send_template_message(
        self,
        to_phone: str,
        template_name: str,
        language_code: str = "he",
        components: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Send a template message via WhatsApp.

        Args:
            to_phone: Phone number in E.164 format
            template_name: Name of the approved template
            language_code: Language code for the template
            components: Template components (header, body, button parameters)

        Returns:
            The API response containing message ID
        """
        url = f"{META_API_BASE_URL}/{self.phone_id}/messages"

        normalized_phone = to_phone.lstrip("+")

        payload: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": normalized_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
            },
        }

        if components:
            payload["template"]["components"] = components

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                logger.info(
                    "whatsapp_template_sent",
                    to=normalized_phone,
                    template=template_name,
                    message_id=data.get("messages", [{}])[0].get("id"),
                )
                return data
            except httpx.HTTPStatusError as e:
                error_data = e.response.json() if e.response.content else {}
                logger.error(
                    "meta_api_error",
                    status_code=e.response.status_code,
                    error=error_data,
                )
                raise MetaAPIError(f"Meta API error: {error_data}") from e
            except httpx.HTTPError as e:
                logger.error("meta_http_error", error=str(e))
                raise MetaAPIError(f"HTTP error communicating with Meta: {e}") from e


meta_service = MetaService()
