"""Custom exceptions for the application."""


class LeadAutomationError(Exception):
    """Base exception for all application errors."""

    pass


class MondayAPIError(LeadAutomationError):
    """Error communicating with Monday.com API."""

    pass


class MetaAPIError(LeadAutomationError):
    """Error communicating with Meta WhatsApp API."""

    pass


class WebhookValidationError(LeadAutomationError):
    """Invalid webhook payload received."""

    pass


class LeadNotFoundError(LeadAutomationError):
    """Lead not found in database."""

    pass
