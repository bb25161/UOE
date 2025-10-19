# File: src/interfaces.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

# --- OOP Concept: Abstraction & Interface Definition ---
# These Abstract Base Classes (ABCs) define contracts (interfaces) for components.
# They specify *what* methods implementing classes must provide, but not *how*.
# This is a core example of Abstraction in OOP.
# It also forms the basis for the Dependency Inversion Principle (DIP) of SOLID,
# as higher-level modules will depend on these abstractions, not concrete classes.
# Ref: Martin, R. C. (2008) Clean Code.
# Ref: NIST SP 800-160 Vol. 1 - Encourages modular design via interfaces.

# --- Class Definition ---
class LogSource(ABC):
    """
    Abstract Base Class (Interface) for log sources.
    Defines the contract for retrieving logs.
    OOP Principle: Abstraction.
    """
    # --- Abstract Method Definition (Contract) ---
    @abstractmethod
    def get_logs(self) -> List[Dict[str, Any]]:
        """Retrieve logs as a list of dictionaries."""
        pass

# --- Class Definition ---
class FraudDetector(ABC):
    """
    Abstract Base Class (Interface) for fraud detection logic.
    Defines the contract for anomaly checking.
    OOP Principle: Abstraction.
    Allows for different detection strategies (Polymorphism) adhering to LSP.
    """
    # --- Abstract Method Definition (Contract) ---
    @abstractmethod
    def is_anomaly(self, log_entry: Dict[str, Any]) -> bool:
        """Check a single log entry for anomalies. Returns True if anomalous."""
        pass

# --- Class Definition ---
class NotificationChannel(ABC):
    """
    Abstract Base Class (Interface) for notification channels.
    Defines the contract for sending alerts.
    OOP Principle: Abstraction.
    Supports Open/Closed Principle (OCP) - new channels can be added without modifying the service.
    """
    # --- Abstract Method Definition (Contract) ---
    @abstractmethod
    def send_alert(self, message: str, log_entry: Dict[str, Any]) -> None:
        """Send an alert message regarding a specific log entry."""
        pass