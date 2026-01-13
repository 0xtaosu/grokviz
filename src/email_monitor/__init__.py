"""Email monitoring module for fetching and parsing Grok daily emails."""

from src.email_monitor.client import EmailClient
from src.email_monitor.parser import EmailParser

__all__ = ["EmailClient", "EmailParser"]
