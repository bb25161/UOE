# File: src/ai_detector.py

import logging
from typing import Dict, Any
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

# Import the interface it implements
from src.interfaces import FraudDetector

logger = logging.getLogger(__name__)

class VertexAIDetector(FraudDetector):
    """
    Concrete implementation of FraudDetector using Google Cloud Vertex AI Anomaly Detection.
    OOP Principle: Implements FraudDetector interface. Encapsulation. LSP compliant.
    Ref: Google Cloud Vertex AI Documentation.
    Security Note: Relies on ADC or service account permissions. Manage endpoint details securely.
    """
    def __init__(self, project: str, endpoint_id: str, location: str = "europe-west4"):
        """Initializes the Vertex AI client and endpoint."""
        if not project or not endpoint_id:
            raise ValueError("GCP Project ID and Vertex AI Endpoint ID are required.")
        self.project = project
        self.endpoint_id = endpoint_id
        self.location = location
        try:
            aiplatform.init(project=project, location=location)
            endpoint_name = f"projects/{project}/locations/{location}/endpoints/{endpoint_id}"
            self._endpoint = aiplatform.Endpoint(endpoint_name)
            logger.info(f"VertexAIDetector initialized for endpoint: {endpoint_name}")
        except ImportError:
            logger.error("google-cloud-aiplatform library not found. Run 'pip install google-cloud-aiplatform'.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI client/endpoint: {e}", exc_info=True)
            raise

    # --- Method Implementation (Fulfilling Contract - AI Strategy) ---
    # This is the AI-based implementation of the is_anomaly check.
    def is_anomaly(self, log_entry: Dict[str, Any]) -> bool:
        """Sends the log entry data to Vertex AI for anomaly prediction."""
        try:
            # --- Data Preparation (Adapt based on your model's expected features) ---
            instance_data = {
                # Ensure keys match the feature names used during model training
                "amount": log_entry.get("amount", 0.0),
                # Add other features expected by your model, e.g.:
                # "feature2": log_entry.get("some_other_field", default_value),
            }
            if not instance_data: # Basic check
                 logger.warning(f"No valid features extracted from log {log_entry.get('tx_id')} for Vertex AI.")
                 return False

            instance_protobuf = json_format.ParseDict(instance_data, Value())
            instances = [instance_protobuf]
            logger.debug(f"Sending instance to Vertex AI: {instance_data}")

            # --- API Call ---
            prediction_response = self._endpoint.predict(instances=instances)
            logger.debug(f"Vertex AI raw response: {prediction_response}")

            # --- Response Parsing (Adapt based on your model's output format) ---
            if not prediction_response.predictions:
                logger.warning(f"Vertex AI returned no predictions for tx {log_entry.get('tx_id')}")
                return False

            prediction_result = prediction_response.predictions[0] # Assuming one prediction per instance

            # Example Parsing Logic (MUST BE ADJUSTED)
            anomaly_score = prediction_result.get('anomaly_score')
            if anomaly_score is not None:
                anomaly_threshold = 0.85 # Tune this threshold
                is_anomalous = anomaly_score > anomaly_threshold
                logger.info(f"Tx {log_entry.get('tx_id')} - Vertex AI Score: {anomaly_score:.4f}, Anomaly: {is_anomalous} (Threshold: {anomaly_threshold})")
                return is_anomalous

            is_anomalous_flag = prediction_result.get('is_anomaly') # Adjust key if needed
            if isinstance(is_anomalous_flag, bool):
                logger.info(f"Tx {log_entry.get('tx_id')} - Vertex AI Flag: {is_anomalous_flag}")
                return is_anomalous_flag

            logger.warning(f"Could not parse Vertex AI prediction for tx {log_entry.get('tx_id')}: {prediction_result}")
            return False

        except ValueError as ve:
            logger.error(f"Data formatting error for Vertex AI prediction (Tx: {log_entry.get('tx_id')}): {ve}", exc_info=True)
            return False # Treat formatting errors as non-anomalous
        except Exception as e:
            logger.error(f"Error calling Vertex AI endpoint for tx {log_entry.get('tx_id')}: {e}", exc_info=True)
            # Implement fallback strategy or circuit breaker if needed
            return False # Treat API errors as non-anomalous for safety