"""Pydantic schemas for Meta WhatsApp webhook payloads."""

from typing import Any

from pydantic import BaseModel


class MetaWebhookMessage(BaseModel):
    """Individual message in Meta webhook payload."""

    from_: str | None = None  # sender phone number
    id: str
    timestamp: str
    type: str
    text: dict[str, str] | None = None

    class Config:
        populate_by_name = True
        fields = {"from_": "from"}


class MetaWebhookContact(BaseModel):
    """Contact information in Meta webhook."""

    profile: dict[str, str] | None = None
    wa_id: str


class MetaWebhookValue(BaseModel):
    """Value object in Meta webhook changes."""

    messaging_product: str
    metadata: dict[str, str]
    contacts: list[MetaWebhookContact] | None = None
    messages: list[MetaWebhookMessage] | None = None
    statuses: list[dict[str, Any]] | None = None


class MetaWebhookChange(BaseModel):
    """Change object in Meta webhook."""

    value: MetaWebhookValue
    field: str


class MetaWebhookEntry(BaseModel):
    """Entry object in Meta webhook payload."""

    id: str
    changes: list[MetaWebhookChange]


class MetaWebhookPayload(BaseModel):
    """Full Meta WhatsApp webhook payload."""

    object: str
    entry: list[MetaWebhookEntry]


class MetaWebhookVerification(BaseModel):
    """Meta webhook verification query parameters."""

    hub_mode: str | None = None
    hub_verify_token: str | None = None
    hub_challenge: str | None = None

    class Config:
        populate_by_name = True
        fields = {
            "hub_mode": "hub.mode",
            "hub_verify_token": "hub.verify_token",
            "hub_challenge": "hub.challenge",
        }
