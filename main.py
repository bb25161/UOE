# File: main.py

import logging
import os
from typing import List

# Import concrete implementations and the service
# Assuming the 'src' directory is in the same level as main.py



from src.services import FraudMonitoringService
from src.interfaces import LogSource, FraudDetector, NotificationChannel # Needed for type hint

# Configure basic logging for the main application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Application Entry Point / Composition Root.
    Configures, creates, and injects dependencies, then runs the service.
    Includes configuration options for Rule-based vs Vertex AI detector.
    Ref: OWASP A05:2021 Security Misconfiguration - Use environment variables for config.
    """
    logger.info("Setting up the Fraud Monitoring System...")

    try:
        # --- Configuration (Read from Environment Variables or use defaults) ---
        log_source_type = os.getenv("LOG_SOURCE_TYPE", "simple_list")
        detector_type = os.getenv("DETECTOR_TYPE", "rule_based") # Set to 'ai_vertex' via env var to use AI

        # Rule-based detector config
        detector_threshold_str = os.getenv("DETECTOR_THRESHOLD", "4000.0")
        try:
            detector_threshold = float(detector_threshold_str)
        except ValueError:
            logger.warning(f"Invalid DETECTOR_THRESHOLD env var '{detector_threshold_str}', using default 4000.0")
            detector_threshold = 4000.0

        # Vertex AI detector config (REQUIRED if detector_type is 'ai_vertex')
        gcp_project = os.getenv("GCP_PROJECT")
        vertex_endpoint_id = os.getenv("VERTEX_ENDPOINT_ID")
        vertex_location = os.getenv("VERTEX_LOCATION", "europe-west4") # Example region

        # Notification config
        alert_email_recipient = os.getenv("ALERT_EMAIL", "alert-team@example.com")
        # Securely retrieve real credentials for IVR etc. in production
        ivr_number = os.getenv("IVR_NUMBER", "+1234567890") # Default for simulation
        ivr_sid = os.getenv("TWILIO_SID", "ACxxxx_placeholder")
        ivr_token = os.getenv("TWILIO_TOKEN", "authxxxx_placeholder")

        # --- Dependency Creation (Wiring based on configuration) ---
        logger.info(f"Configuring Log Source: {log_source_type}")
        log_source: LogSource
        if log_source_type == "simple_list":
            log_source = SimpleListLogSource()
        # elif log_source_type == "file": # Example for future extension
            # filepath = os.getenv("LOG_FILEPATH")
            # if not filepath: raise ValueError("LOG_FILEPATH env var must be set for file log source.")
            # log_source = FileLogSource(filepath=filepath) # Assuming FileLogSource is implemented
        else:
            raise ValueError(f"Unknown log_source_type configured: {log_source_type}")

        logger.info(f"Configuring Detector: {detector_type}")
        fraud_detector: FraudDetector
        if detector_type == "rule_based":
            fraud_detector = SimpleRuleBasedDetector(amount_threshold=detector_threshold)
        elif detector_type == "ai_vertex":
            if not gcp_project or not vertex_endpoint_id:
                raise ValueError("GCP_PROJECT and VERTEX_ENDPOINT_ID env vars must be set for ai_vertex detector.")
            try:
                # OOP Principle: Instantiating the AI Detector class
                fraud_detector = VertexAIDetector(
                    project=gcp_project,
                    endpoint_id=vertex_endpoint_id,
                    location=vertex_location
                )
                logger.info(f"Vertex AI detector configured for project {gcp_project}, endpoint {vertex_endpoint_id[:5]}...")
            except Exception as ai_init_error:
                logger.critical(f"Fatal: Failed to initialize Vertex AI Detector: {ai_init_error}", exc_info=True)
                raise # Stop execution if AI detector fails to initialize
        else:
            raise ValueError(f"Unknown detector_type configured: {detector_type}")

        # Creating notification channel objects
        # OOP Principle: Polymorphism - adding different channel types to the same list
        notification_channels: List[NotificationChannel] = []
        logger.info("Configuring Notification Channels...")
        if alert_email_recipient:
            try:
                # OOP Principle: Instantiating Email channel object
                notification_channels.append(EmailNotificationChannel(recipient_email=alert_email_recipient))
                logger.info("Email notification channel added.")
            except ValueError as e:
                logger.error(f"Skipping Email channel configuration due to error: {e}")

        try:
            # OOP Principle: Instantiating IVR channel object
            # Using placeholder/default credentials for simulation unless env vars are set
            notification_channels.append(IVRNotificationChannel(ivr_service_number=ivr_number, account_sid=ivr_sid, auth_token=ivr_token))
            logger.info("IVR notification channel added (simulated).")
        except ValueError as e:
            logger.error(f"Skipping IVR channel configuration due to error: {e}")

        if not notification_channels:
             logger.error("Critical: No notification channels were configured successfully. System cannot send alerts.")
             return # Exit if no way to notify

        # --- Dependency Injection (Manual Constructor Injection) ---
        # Passing the created concrete objects (dependencies) into the service.
        # The service depends on abstractions (interfaces), enabling this flexibility.
        logger.info("Injecting dependencies into FraudMonitoringService...")
        monitoring_service = FraudMonitoringService(
            log_source=log_source,
            detector=fraud_detector,
            channels=notification_channels
        )

        logger.info("System setup complete. Starting monitoring cycle...")
        # --- Run Core Application Logic ---
        # OOP Principle: Calling methods on the composed object (service)
        monitoring_service.monitor_and_alert()

        logger.info("Monitoring cycle finished.")

    except (ValueError, TypeError) as config_error:
        # Catching specific configuration/initialization errors
        logger.critical(f"Configuration or Initialization Error: {config_error}", exc_info=False) # No need for full stack trace here usually
        logger.critical("Please check environment variables and configuration.")
    except ImportError as import_err:
        logger.critical(f"Missing Dependency Error: {import_err}. Have you installed requirements.txt?", exc_info=False)
    except Exception as general_error:
        # Catching any other unexpected errors during setup or runtime
        logger.critical(f"An unexpected critical error occurred: {general_error}", exc_info=True) # Log full trace


if __name__ == "__main__":
    # Standard Python entry point.
    main()