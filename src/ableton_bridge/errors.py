"""Custom exceptions for Ableton Bridge."""


class AbletonOSCError(RuntimeError):
    """Raised when AbletonOSC cannot be reached or returns an error."""
