# File: src/services.py
import logging
from typing import List, Dict, Any
from src.interfaces import LogSource, FraudDetector, NotificationChannel

logger = logging.getLogger(__name__)

class FraudMonitoringService:
    def __init__(self, log_source: LogSource, detector: FraudDetector, channels: List[NotificationChannel]):
        if not isinstance(log_source, LogSource):
            raise TypeError("log_source must implement the LogSource interface.")
        if not isinstance(detector, FraudDetector):
            raise TypeError("detector must implement the FraudDetector interface.")
        if not channels or not all(isinstance(ch, NotificationChannel) for ch in channels):
            raise TypeError("channels must be a non-empty list of NotificationChannel implementations.")

        self._log_source = log_source
        self._detector = detector
        self._channels = channels
        logger.info("FraudMonitoringService initialized successfully.")

    def monitor_and_alert(self):
        logger.info("Starting fraud monitoring cycle...")
        try:
            logs = self._log_source.get_logs()
            logger.info(f"Fetched {len(logs)} log entries.")
            anomaly_count = 0

            for entry in logs:
                required_keys = ["tx_id", "user_id", "amount"]
                if not all(key in entry for key in required_keys):
                    logger.warning(f"Skipping log entry due to missing required keys: {entry}")
                    continue

                if self._detector.is_anomaly(entry):
                    anomaly_count += 1
                    logger.warning(f"⚠️ ANOMALY DETECTED: Tx ID {entry['tx_id']} | Amount: {entry['amount']}")
                    message = f"Potential fraudulent activity detected for transaction {entry['tx_id']}."
                    for channel in self._channels:
                        channel.send_alert(message, entry)

            if anomaly_count == 0:
                logger.info("No anomalies detected in this cycle.")
            else:
                logger.warning(f"Detected {anomaly_count} anomalies in this cycle.")

        except Exception as e:
            logger.error(f"Critical error fetching logs: {e}", exc_info=True)
        logger.info("Fraud monitoring cycle finished.")
