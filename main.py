# File: main.py
import logging
import os
import time
from typing import List

from src.implementations import (
    SimpleListLogSource,
    SimpleRuleBasedDetector,
    EmailNotificationChannel,
    IVRNotificationChannel,
    summarize_detection
)
from src.ai_detector import VertexAIDetector
from src.services import FraudMonitoringService
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


# --- Logging yapılandırması ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True  # Önceden tanımlı handler'ları sıfırlar
)
logger = logging.getLogger(__name__)


def main():
    """Main application entry point"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}💡 Fraud Detection Simulation System (University of Essex)")
    print(f"{Fore.CYAN}{'-'*60}")
    print(f"{Fore.WHITE}This program simulates the detection of fraud anomalies\n"
          f"in mobile app transaction logs. It identifies suspicious\n"
          f"activities and simulates sending alerts via Email and IVR calls.\n"
          f"(No user input required – all actions are automated.)")
    print(f"{Fore.CYAN}{'='*60}\n{Style.RESET_ALL}")

    start_time = time.time()
    logger.info("Setting up the Fraud Monitoring System...")

    try:
        # --- Configuration ---
        log_source_type = os.getenv("LOG_SOURCE_TYPE", "simple_list")
        detector_type = os.getenv("DETECTOR_TYPE", "rule_based")

        detector_threshold_str = os.getenv("DETECTOR_THRESHOLD", "4000.0")
        try:
            detector_threshold = float(detector_threshold_str)
        except ValueError:
            logger.warning(f"Invalid DETECTOR_THRESHOLD '{detector_threshold_str}', using default 4000.0")
            detector_threshold = 4000.0

        gcp_project = os.getenv("GCP_PROJECT")
        vertex_endpoint_id = os.getenv("VERTEX_ENDPOINT_ID")
        vertex_location = os.getenv("VERTEX_LOCATION", "europe-west4")

        alert_email_recipient = os.getenv("ALERT_EMAIL", "alert-team@example.com")
        ivr_number = os.getenv("IVR_NUMBER", "+1234567890")
        ivr_sid = os.getenv("TWILIO_SID", "ACxxxx_placeholder")
        ivr_token = os.getenv("TWILIO_TOKEN", "authxxxx_placeholder")

        # --- Log Source ---
        logger.info(f"Configuring Log Source: {log_source_type}")
        if log_source_type == "simple_list":
            log_source = SimpleListLogSource()
        else:
            raise ValueError(f"Unknown log_source_type: {log_source_type}")

        # --- Detector ---
        logger.info(f"Configuring Detector: {detector_type}")
        if detector_type == "rule_based":
            fraud_detector = SimpleRuleBasedDetector(threshold=detector_threshold)
        elif detector_type == "ai_vertex":
            if not gcp_project or not vertex_endpoint_id:
                raise ValueError("GCP_PROJECT and VERTEX_ENDPOINT_ID must be set for ai_vertex detector.")
            fraud_detector = VertexAIDetector(
                project=gcp_project,
                endpoint_id=vertex_endpoint_id,
                location=vertex_location
            )
        else:
            raise ValueError(f"Unknown detector_type: {detector_type}")

        # --- Notification Channels ---
        logger.info("Configuring Notification Channels...")
        notification_channels: List[NotificationChannel] = []

        if alert_email_recipient:
            notification_channels.append(
                EmailNotificationChannel(recipient_email=alert_email_recipient)
            )
            logger.info(f"{Fore.GREEN}📧 Email notification channel added.")

        notification_channels.append(
            IVRNotificationChannel(
                ivr_service_number=ivr_number,
                account_sid=ivr_sid,
                auth_token=ivr_token
            )
        )
        logger.info(f"{Fore.GREEN}📞 IVR notification channel added (simulated).")

        # --- Fraud Monitoring Service Initialization ---
        monitoring_service = FraudMonitoringService(
            log_source=log_source,
            detector=fraud_detector,
            channels=notification_channels
        )
        logger.info("FraudMonitoringService initialized successfully.")

        # --- Run Main Logic ---
        logger.info("Starting monitoring cycle...\n")
        logs = log_source.get_logs()
        anomalies = fraud_detector.detect(logs)

        for anomaly in anomalies:
            message = "Fraud alert detected!"
            for channel in notification_channels:
                channel.send_alert(message, anomaly)

        summarize_detection(logs, anomalies, start_time)

        elapsed = time.time() - start_time
        logger.info(f"{Fore.CYAN}✅ Fraud monitoring cycle completed in {elapsed:.2f} seconds.")

    except Exception as e:
        logger.critical(f"{Fore.RED}❌ Critical Error: {e}", exc_info=True)


if __name__ == "__main__":
    print(">>> Debug: main.py started")
    main()
    print(">>> Debug: main() execution finished")
