# ================================================================
# File: services.py
# Description:
#   Core service class that coordinates log reading, anomaly detection,
#   and alert notifications.
# ================================================================

import logging
import time
from typing import List
from src.interfaces import LogSource, FraudDetector, NotificationChannel

logger = logging.getLogger(__name__)

# ================================================================
# Class: FraudMonitoringService
# Purpose:
#   Demonstrates Dependency Injection, Encapsulation, and Composition.
# ================================================================
class FraudMonitoringService:
    """Core orchestrator class connecting all subsystems.

    This class receives external dependencies through its constructor
    (Dependency Injection), promoting loose coupling and testability.
    """

    def __init__(self, log_source: LogSource, detector: FraudDetector, channels: List[NotificationChannel]):
        # Encapsulation: internal attributes hidden from external modules
        self.log_source = log_source
        self.detector = detector
        self.channels = channels

        logger.info("FraudMonitoringService initialized successfully.")

    # ================================================================
    # Method: monitor_and_alert
    # Purpose:
    #   Coordinates the main fraud detection workflow.
    # ================================================================
    def monitor_and_alert(self):
        logger.info(f"Fetching logs from {self.log_source.__class__.__name__}...")
        print("🔍 Fetching logs...")

        logs = self.log_source.get_logs()
        print("⚙️  Running fraud detection rules...")

        anomalies = []
        start_time = time.time()

        for entry in logs:
            if self.detector.is_anomaly(entry):
                anomalies.append(entry)
                logger.warning(f"⚠️ ANOMALY DETECTED: Tx ID {entry['tx_id']} | Amount: {entry['amount']} | User: {entry['user_id']}")
                print(f"⚠️  ANOMALY: Tx ID {entry['tx_id']} | Amount: {entry['amount']} | User: {entry['user_id']}")
                self._notify_all(entry)

        duration = time.time() - start_time

        print("\n============================================================")
        print("📊 Fraud Detection Summary")
        print("------------------------------------------------------------")
        print(f"Total logs processed   : {len(logs)}")
        print(f"Detected anomalies     : {len(anomalies)}")
        print(f"Detection duration     : {duration:.3f} seconds")
        print("============================================================\n")

        logger.info(f"Summary -> Logs: {len(logs)}, Anomalies: {len(anomalies)}, Duration: {duration:.3f}s")

    # ================================================================
    # Private Method: _notify_all
    # Purpose:
    #   Send alerts through all available NotificationChannel instances.
    # ================================================================
    def _notify_all(self, log_entry):
        message = f"Fraud alert detected! | Tx ID: {log_entry['tx_id']}, User: {log_entry['user_id']}, Amount: {log_entry['amount']}"

        for channel in self.channels:
            try:
                channel.send_alert(message, log_entry)
            except Exception as e:
                logger.error(f"❌ Failed to send via {channel.__class__.__name__}: {e}")
