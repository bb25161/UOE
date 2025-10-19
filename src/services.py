# File: src/services.py

import logging
from typing import List, Dict, Any
# Depend on abstractions, not concrete classes (DIP)
from src.interfaces import LogSource, FraudDetector, NotificationChannel

# Get logger for this module
logger = logging.getLogger(__name__)

# --- Class Definition ---
class FraudMonitoringService:
    """
    Core service orchestrating the fraud monitoring process.
    OOP Principle: Encapsulation (manages internal state via injected dependencies).
    OOP Principle: Uses Dependency Injection for Loose Coupling.
    SOLID Principle: Adheres to Single Responsibility Principle (SRP).
    SOLID Principle: Adheres to Dependency Inversion Principle (DIP).
    Ref: NIST SP 800-218 (SSDF) - Practice PW.5: Reuse secure components.
    """
    # --- Constructor Method (__init__) & Dependency Injection ---
    def __init__(self,
                 log_source: LogSource,
                 detector: FraudDetector,
                 channels: List[NotificationChannel]):
        # Type checking for dependencies against interfaces (Contracts)
        if not isinstance(log_source, LogSource):
            raise TypeError("log_source must implement the LogSource interface.")
        if not isinstance(detector, FraudDetector):
            raise TypeError("detector must implement the FraudDetector interface.")
        if not channels or not all(isinstance(ch, NotificationChannel) for ch in channels):
            raise TypeError("channels must be a non-empty list of NotificationChannel implementations.")

        # --- OOP Concept: Encapsulation ---
        self._log_source = log_source
        self._detector = detector
        self._channels = channels
        logger.info("FraudMonitoringService initialized successfully.")

    # --- Method Implementation (Core Logic) ---
    def monitor_and_alert(self):
        """Fetches logs, checks anomalies, and sends alerts."""
        logger.info("Starting fraud monitoring cycle...")
        try:
            logs = self._log_source.get_logs() # Uses injected log source (Abstraction)
            logger.info(f"Fetched {len(logs)} log entries.")

            anomaly_count = 0
            for entry in logs:
                # Basic Input Validation (Secure Coding Practice - OWASP Input Validation)
                required_keys = ["tx_id", "user_id", "amount"]
                if not all(key in entry for key in required_keys):
                    logger.warning(f"Skipping log entry due to missing required keys: {entry}")
                    continue

                try:
                    # Uses the injected detector (Abstraction, DI)
                    if self._detector.is_anomaly(entry):
                        anomaly_count += 1
                        logger.warning(f"ANOMALY DETECTED: Tx ID {entry.get('tx_id')} by {type(self._detector).__name__}")
                        alert_message = f"Potential fraudulent activity detected for transaction {entry.get('tx_id')}."

                        # --- OOP Concept: Polymorphism in Action ---
                        # Call send_alert on each channel object, regardless of its concrete type.
                        for channel in self._channels:
                            try:
                                channel.send_alert(alert_message, entry)
                            except Exception as e:
                                logger.error(f"Error sending alert via {type(channel).__name__} for tx {entry.get('tx_id')}: {e}", exc_info=True)
                except Exception as detect_error:
                    logger.error(f"Error during anomaly detection for tx {entry.get('tx_id')}: {detect_error}", exc_info=True)

            # Log summary of the cycle
            if anomaly_count == 0:
                logger.info("No anomalies detected in this cycle.")
            else:
                logger.warning(f"Detected {anomaly_count} anomalies in this cycle.")

        except Exception as source_error:
            logger.error(f"Critical error fetching logs from source: {source_error}", exc_info=True)
            # Consider adding alerting for source failures

        logger.info("Fraud monitoring cycle finished.")