# File: src/interfaces.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

# --- Interface for Log Sources ---
class LogSource(ABC):
    """Abstract interface defining how logs are fetched."""
    @abstractmethod
    def get_logs(self) -> List[Dict[str, Any]]:
        """Return a list of log entries (dictionaries)."""
        pass


# --- Interface for Fraud Detectors ---
class FraudDetector(ABC):
    """Abstract interface defining the fraud detection contract."""
    @abstractmethod
    def is_anomaly(self, log_entry: Dict[str, Any]) -> bool:
        """Return True if the given log entry indicates potential fraud."""
        pass


# --- Interface for Notification Channels ---
class NotificationChannel(ABC):
    """Abstract interface for alerting channels (email, IVR, etc.)."""
    @abstractmethod
    def send_alert(self, message: str, log_entry: Dict[str, Any]) -> None:
        """Send an alert message based on the given log entry."""
        pass
