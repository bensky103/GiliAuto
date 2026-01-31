"""Pydantic schemas for Monday.com webhook payloads."""

from typing import Any

from pydantic import BaseModel


class MondayWebhookEvent(BaseModel):
    """Monday.com webhook event payload."""

    userId: int | None = None
    originalTriggerUuid: str | None = None
    boardId: int
    groupId: str | None = None
    pulseId: int  # This is the item ID
    pulseName: str | None = None
    columnId: str | None = None
    columnType: str | None = None
    columnTitle: str | None = None
    value: dict[str, Any] | None = None
    previousValue: dict[str, Any] | None = None
    changedAt: float | None = None
    isTopGroup: bool | None = None
    triggerTime: str | None = None


class MondayWebhookPayload(BaseModel):
    """Full Monday.com webhook payload wrapper."""

    event: MondayWebhookEvent
    challenge: str | None = None


class MondayWebhookChallenge(BaseModel):
    """Monday.com webhook challenge (for verification)."""

    challenge: str
