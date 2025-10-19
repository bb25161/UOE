# File: src/implementations.py

import logging
from typing import List, Dict, Any
# import smtplib # For real email example
# from twilio.rest import Client # For real IVR example

# Import interfaces defined previously
from src.interfaces import LogSource, FraudDetector, NotificationChannel

logger = logging.getLogger(__name__)

# --- OOP Concept: Class Definition & Inheritance (Interface Implementation) ---
# Concrete classes implement the contracts defined by the abstract classes (interfaces).

# --- Class Definition & Inheritance ---
class SimpleListLogSource(LogSource):
    """
    Concrete implementation of LogSource using a hardcoded list.
    OOP Principle: Implements LogSource interface (Inheritance from ABC).
    """
    # --- Method Implementation (Fulfilling Contract) ---
    def get_logs(self) -> List[Dict[str, Any]]:
        """Returns a hardcoded list of sample logs."""
        logger.info("Fetching logs from SimpleListLogSource...")
        # Sample data including phone numbers for IVR simulation
        return [
            {"tx_id": "t1001", "user_id": "u001", "amount": 150.75, "ip": "192.168.1.10", "device": "Android", "phone": "+905000000001"},
            {"tx_id": "t1002", "user_id": "u002", "amount": 5500.00, "ip": "10.0.0.5", "device": "iOS", "phone": "+905000000002"}, # Potential anomaly
            {"tx_id": "t1003", "user_id": "u001", "amount": 50.00, "ip": "192.168.1.10", "device": "Android", "phone": "+905000000001"},
            {"tx_id": "t1004", "user_id": "u003", "amount": 10.00, "ip": "88.54.12.99", "device": "Web", "phone": None}, # No phone
            {"tx_id": "t1005", "user_id": "u002", "amount": 12000.00, "ip": "212.15.67.81", "device": "iOS", "phone": "+905000000002"}, # Potential anomaly
        ]

# --- Class Definition & Inheritance ---
class SimpleRuleBasedDetector(FraudDetector):
    """
    Concrete implementation of FraudDetector using a simple amount threshold rule.
    OOP Principle: Implements FraudDetector interface (Inheritance from ABC).
    OOP Principle: Encapsulation (hides threshold).
    Ref: OWASP Secure Coding Practices - Input Validation.
    """
    # --- Constructor Method (__init__) ---
    def __init__(self, amount_threshold: float = 5000.0):
        # --- OOP Concept: Encapsulation ---
        if not isinstance(amount_threshold, (int, float)) or amount_threshold <= 0:
            raise ValueError("Amount threshold must be a positive number.")
        self._threshold = amount_threshold
        logger.info(f"SimpleRuleBasedDetector initialized with threshold: {self._threshold}")

    # --- Method Implementation (Fulfilling Contract & Business Logic) ---
    def is_anomaly(self, log_entry: Dict[str, Any]) -> bool:
        """Checks if the transaction amount exceeds the defined threshold."""
        amount = log_entry.get("amount", 0.0)
        # Basic input type validation (Secure Coding Practice)
        if not isinstance(amount, (int, float)) or amount < 0:
            logger.warning(f"Invalid or negative amount in log entry {log_entry.get('tx_id')}. Skipping check.")
            return False

        is_high_amount = amount > self._threshold
        logger.debug(f"Checked Tx: {log_entry.get('tx_id')}, Amount: {amount}, Threshold: {self._threshold}, Is Anomaly: {is_high_amount}")
        return is_high_amount

    def get_threshold(self) -> float: # Optional Getter
        return self._threshold

# --- Class Definition & Inheritance ---
class EmailNotificationChannel(NotificationChannel):
    """
    Concrete implementation for sending alerts via Email (Simulated).
    OOP Principle: Implements NotificationChannel interface. Encapsulation. Polymorphism.
    """
    def __init__(self, recipient_email: str):
        # OOP Principle: Encapsulation - Internal state `_recipient`
        if not recipient_email or "@" not in recipient_email: # Basic format check
             raise ValueError("Invalid recipient email format provided.")
        self._recipient = recipient_email
        logger.info(f"EmailNotificationChannel configured for recipient: {self._recipient}")
        # Real impl needs secure credential management (OWASP Credential Management)

    # --- Method Implementation (Polymorphic Behavior) ---
    def send_alert(self, message: str, log_entry: Dict[str, Any]) -> None:
        """Simulates sending an email alert."""
        subject = f"Fraud Alert Detected: Transaction {log_entry.get('tx_id')}"
        body = f"Alert Message: {message}\n\nTransaction Details:\nUser ID: {log_entry.get('user_id')}\nAmount: {log_entry.get('amount')}\nIP Address: {log_entry.get('ip')}\nDevice: {log_entry.get('device')}"
        logger.info(f"--- SIMULATING SENDING EMAIL To: {self._recipient} ---")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body:\n{body}")
        logger.info(f"--- EMAIL SIMULATION COMPLETE ---")

# --- Class Definition & Inheritance ---
class IVRNotificationChannel(NotificationChannel):
    """
    Concrete implementation for initiating an IVR call (Simulated).
    OOP Principle: Implements NotificationChannel interface. Encapsulation. Polymorphism.
    """
    def __init__(self, ivr_service_number: str = "+1234567890", account_sid: str = "ACxxxx_placeholder", auth_token: str = "authxxxx_placeholder"):
        # OOP Principle: Encapsulation - Internal state including placeholders
        if not ivr_service_number:
            raise ValueError("IVR Service number cannot be empty.")
        self._service_number = ivr_service_number
        self._account_sid = account_sid # Placeholder! Securely manage real credentials.
        self._auth_token = auth_token   # Placeholder! Ref: OWASP A05:2021 Security Misconfiguration
        logger.info(f"IVRNotificationChannel configured with service number: {self._service_number}")

    # --- Method Implementation (Polymorphic Behavior) ---
    def send_alert(self, message: str, log_entry: Dict[str, Any]) -> None:
        """Simulates initiating an IVR call."""
        user_phone = log_entry.get("phone")
        if not user_phone:
            logger.warning(f"No phone number found for user {log_entry.get('user_id')} in log {log_entry.get('tx_id')}. Cannot make IVR call.")
            return

        call_message = f"Suspicious activity detected for user {log_entry.get('user_id')}. Transaction amount: {log_entry.get('amount')}. {message} Please press 1 if this transaction was not made by you."
        logger.info(f"--- SIMULATING INITIATING IVR CALL To: {user_phone} ---")
        logger.info(f"Using Account SID (Placeholder): {self._account_sid[:5]}...")
        logger.info(f"Calling From: {self._service_number}")
        logger.info(f"Message to Play (TwiML simulation): {call_message}")
        logger.info(f"--- IVR CALL SIMULATION COMPLETE ---")
        # Real implementation would use Twilio API