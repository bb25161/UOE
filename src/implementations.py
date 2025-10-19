import logging
import os
import time
from typing import Dict, Any
from src.interfaces import LogSource, FraudDetector, NotificationChannel

# --- Renkli terminal desteği ---
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore:
        GREEN = YELLOW = RED = CYAN = MAGENTA = BLUE = WHITE = ""
    class Style:
        RESET_ALL = ""


# --- Log dosyası yapılandırması ---
os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/fraud_monitor.log", mode="a", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(file_handler)


# ===============================================================
# 🔹 Log Source
# ===============================================================
class SimpleListLogSource(LogSource):
    """Simulates a basic transaction log source."""

    def __init__(self):
        self.logs = [
            {"transaction_id": "t1001", "amount": 1200.0, "user_id": "u01"},
            {"transaction_id": "t1002", "amount": 5500.0, "user_id": "u02"},
            {"transaction_id": "t1003", "amount": 350.0, "user_id": "u03"},
            {"transaction_id": "t1004", "amount": 8200.0, "user_id": "u04"},
            {"transaction_id": "t1005", "amount": 420.0, "user_id": "u05"},
        ]

    def get_logs(self):
        logger.info("Fetching logs from SimpleListLogSource...")
        print(f"{Fore.CYAN}🔍 Fetching logs...{Style.RESET_ALL}")
        time.sleep(0.5)
        return self.logs


# ===============================================================
# 🔹 Detector
# ===============================================================
class SimpleRuleBasedDetector(FraudDetector):
    """Detects anomalies using a simple rule threshold."""

    def __init__(self, threshold: float = 5000.0):
        if not isinstance(threshold, (int, float)) or threshold <= 0:
            raise ValueError("Threshold must be a positive number.")
        self.threshold = threshold

    def is_anomaly(self, log):
        """Implements the required abstract method."""
        return log.get("amount", 0) > self.threshold

    def detect(self, logs):
        """Detects all anomalies in a list of logs."""
        anomalies = []
        print(f"{Fore.YELLOW}⚙️  Running fraud detection rules...{Style.RESET_ALL}")
        for log in logs:
            if self.is_anomaly(log):
                anomalies.append(log)
                logger.warning(
                    f"⚠️ ANOMALY DETECTED: Tx ID {log['transaction_id']} | "
                    f"Amount: {log['amount']} | User: {log['user_id']}"
                )
                print(
                    f"{Fore.RED}⚠️  ANOMALY: Tx ID {log['transaction_id']} | "
                    f"Amount: {log['amount']} | User: {log['user_id']}{Style.RESET_ALL}"
                )
        if not anomalies:
            print(f"{Fore.GREEN}✅ No anomalies detected.{Style.RESET_ALL}")
            logger.info("✅ No anomalies detected.")
        return anomalies


# ===============================================================
# 🔹 Notification Channels
# ===============================================================
class EmailNotificationChannel(NotificationChannel):
    """Simulates sending fraud alert emails."""

    def __init__(self, recipient_email: str):
        self.recipient_email = recipient_email

    def send_alert(self, message: str, log_entry: Dict[str, Any]) -> None:
        """Implements NotificationChannel abstract method."""
        self.send(message, log_entry)

    def send(self, message: str, log_entry: Dict[str, Any]) -> None:
        """Simulated email sending with log context."""
        time.sleep(0.2)
        tx = log_entry.get("transaction_id")
        amount = log_entry.get("amount")
        user = log_entry.get("user_id")
        full_message = f"{message} | Tx ID: {tx}, User: {user}, Amount: {amount}"
        print(f"{Fore.MAGENTA}📧 Email sent to {self.recipient_email}: {full_message}{Style.RESET_ALL}")
        logger.info(f"📧 Email sent to {self.recipient_email}: {full_message}")


class IVRNotificationChannel(NotificationChannel):
    """Simulates automated IVR call notifications."""

    def __init__(self, ivr_service_number: str, account_sid: str, auth_token: str):
        self.ivr_service_number = ivr_service_number
        self.account_sid = account_sid
        self.auth_token = auth_token

    def send_alert(self, message: str, log_entry: Dict[str, Any]) -> None:
        """Implements NotificationChannel abstract method."""
        self.send(message, log_entry)

    def send(self, message: str, log_entry: Dict[str, Any]) -> None:
        """Simulated IVR call sending."""
        time.sleep(0.3)
        tx = log_entry.get("transaction_id")
        user = log_entry.get("user_id")
        print(f"{Fore.CYAN}📞 IVR call to {self.ivr_service_number} (simulated): {message} | Tx ID: {tx}, User: {user}{Style.RESET_ALL}")
        logger.info(f"📞 IVR call to {self.ivr_service_number} (simulated): {message} | Tx ID: {tx}, User: {user}")


# ===============================================================
# 🔹 Summary Helper Function
# ===============================================================
def summarize_detection(logs, anomalies, start_time):
    """Prints a runtime summary with color and logs."""
    duration = round(time.time() - start_time, 3)
    total_logs = len(logs)
    total_anomalies = len(anomalies)

    summary = (
        f"\n{Fore.CYAN}{'='*60}\n"
        f"{Fore.YELLOW}📊 Fraud Detection Summary\n"
        f"{Fore.CYAN}{'-'*60}\n"
        f"{Fore.WHITE}Total logs processed   : {total_logs}\n"
        f"Detected anomalies     : {total_anomalies}\n"
        f"Detection duration     : {duration} seconds\n"
        f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n"
    )

    print(summary)
    logger.info(
        f"Summary -> Logs: {total_logs}, Anomalies: {total_anomalies}, Duration: {duration}s"
    )
