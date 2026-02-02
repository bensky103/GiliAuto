"""Monday.com API client service."""

from typing import Any

import httpx

from src.core.config import get_settings
from src.core.exceptions import MondayAPIError
from src.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

MONDAY_API_URL = "https://api.monday.com/v2"

# Status strings (Hebrew) - DO NOT TRANSLATE
STATUS_NEW_LEAD = "לייד חדש"
STATUS_MESSAGE_SENT = "נשלחה הודעה"
STATUS_NO_ANSWER_1 = "אין מענה 1"
STATUS_NO_ANSWER_2 = "אין מענה 2"
STATUS_CUSTOMER_REPLIED = "לקוח הגיב"
STATUS_MEETING_SET = "נקבעה שיחת מכירה"


class MondayService:
    """Service for interacting with Monday.com API."""

    def __init__(self) -> None:
        self.api_key = settings.monday_api_key
        self.board_id = settings.monday_board_id
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }

    async def _execute_query(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a GraphQL query against Monday.com API."""
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    MONDAY_API_URL,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                if "errors" in data:
                    logger.error("monday_api_error", errors=data["errors"])
                    raise MondayAPIError(f"Monday API error: {data['errors']}")

                return data
            except httpx.HTTPError as e:
                logger.error("monday_http_error", error=str(e))
                raise MondayAPIError(f"HTTP error communicating with Monday: {e}") from e

    async def get_item(self, item_id: str) -> dict[str, Any]:
        """Fetch an item by ID from Monday.com."""
        query = """
        query GetItem($itemId: [ID!]) {
            items(ids: $itemId) {
                id
                name
                column_values {
                    id
                    text
                    value
                }
            }
        }
        """
        variables = {"itemId": [item_id]}
        result = await self._execute_query(query, variables)

        items = result.get("data", {}).get("items", [])
        if not items:
            raise MondayAPIError(f"Item {item_id} not found")

        return items[0]

    async def get_item_status(self, item_id: str, status_column_id: str = "status") -> str:
        """Get the current status of an item."""
        item = await self.get_item(item_id)
        for col in item.get("column_values", []):
            if col["id"] == status_column_id:
                return col.get("text", "")
        return ""

    async def update_item_status(
        self, item_id: str, status: str, status_column_id: str = "status"
    ) -> dict[str, Any]:
        """Update the status of an item on Monday.com."""
        query = """
        mutation UpdateItemStatus($boardId: ID!, $itemId: ID!, $columnId: String!, $value: JSON!) {
            change_column_value(
                board_id: $boardId,
                item_id: $itemId,
                column_id: $columnId,
                value: $value
            ) {
                id
            }
        }
        """
        # Monday expects status as JSON with "label" key
        import json
        value = json.dumps({"label": status})

        variables = {
            "boardId": self.board_id,
            "itemId": item_id,
            "columnId": status_column_id,
            "value": value,
        }

        logger.info("updating_monday_status", item_id=item_id, new_status=status)
        return await self._execute_query(query, variables)

    async def get_phone_number_from_item(
        self, item_id: str, phone_column_id: str = "phone"
    ) -> str | None:
        """Extract phone number from an item."""
        item = await self.get_item(item_id)
        for col in item.get("column_values", []):
            if col["id"] == phone_column_id:
                # Phone column value is JSON with "phone" key
                value = col.get("value")
                if value:
                    import json
                    try:
                        parsed = json.loads(value)
                        return parsed.get("phone")
                    except (json.JSONDecodeError, TypeError):
                        return col.get("text")
        return None

    async def get_lead_name_from_item(self, item_id: str) -> str:
        """Get the lead name (item name) from Monday.com."""
        item = await self.get_item(item_id)
        return item.get("name", "")


monday_service = MondayService()
