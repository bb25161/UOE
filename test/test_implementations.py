# File: tests/test_implementations.py

import pytest
from src.implementations import SimpleRuleBasedDetector, EmailNotificationChannel, IVRNotificationChannel, SimpleListLogSource
# Assume ai_detector.py exists for import test
try:
    from src.ai_detector import VertexAIDetector
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False


# --- Tests for SimpleListLogSource ---
def test_simple_log_source_returns_list_of_dicts():
    source = SimpleListLogSource()
    logs = source.get_logs()
    assert isinstance(logs, list)
    assert len(logs) > 0
    assert all(isinstance(log, dict) for log in logs)
    # Check for essential keys in the first log entry as a sample
    if logs:
        assert "tx_id" in logs[0]
        assert "user_id" in logs[0]
        assert "amount" in logs[0]


# --- Tests for SimpleRuleBasedDetector ---
@pytest.fixture
def detector():
    """Pytest fixture to create a default detector instance for tests."""
    return SimpleRuleBasedDetector(amount_threshold=5000.0)

def test_detector_anomaly_detected(detector):
    log_entry = {"tx_id": "t001", "amount": 6000.00, "user_id": "u1", "ip": "1.1.1.1"}
    assert detector.is_anomaly(log_entry) is True

def test_detector_no_anomaly(detector):
    log_entry_below = {"tx_id": "t002", "amount": 4999.99, "user_id": "u1", "ip": "1.1.1.1"}
    log_entry_equal = {"tx_id": "t003", "amount": 5000.00, "user_id": "u1", "ip": "1.1.1.1"}
    assert detector.is_anomaly(log_entry_below) is False
    assert detector.is_anomaly(log_entry_equal) is False

def test_detector_invalid_amount(detector, caplog):
    """Test detector's behavior with invalid amount types or negative values."""
    log_entry_str = {"tx_id": "t004", "amount": "invalid", "user_id": "u1"}
    log_entry_neg = {"tx_id": "t005", "amount": -100.0, "user_id": "u1"}
    log_entry_none = {"tx_id": "t006", "user_id": "u1"} # Missing amount

    assert detector.is_anomaly(log_entry_str) is False
    assert detector.is_anomaly(log_entry_neg) is False
    assert detector.is_anomaly(log_entry_none) is False

    # Check if a warning was logged
    assert "Invalid or negative amount" in caplog.text

def test_detector_init_invalid_threshold():
    """Test detector raises error for invalid threshold during initialization."""
    with pytest.raises(ValueError, match="Amount threshold must be a positive number"):
        SimpleRuleBasedDetector(amount_threshold=0)
    with pytest.raises(ValueError, match="Amount threshold must be a positive number"):
        SimpleRuleBasedDetector(amount_threshold=-100)
    # Check for non-numeric type
    with pytest.raises(ValueError): # Should raise ValueError due to check
         SimpleRuleBasedDetector(amount_threshold="invalid")


# --- Tests for Notification Channels (Simulated Output captured via caplog) ---
@pytest.fixture
def sample_log():
    return {"tx_id": "t-alert", "user_id": "u-alert", "amount": 9999.99, "ip": "1.2.3.4", "device": "TestDevice", "phone": "+9059999999"}

def test_email_channel_simulation(caplog, sample_log):
    """Test if the simulated email log output contains expected information."""
    recipient = "test@example.com"
    channel = EmailNotificationChannel(recipient_email=recipient)
    message = "Test Alert Message"
    with caplog.at_level(logging.INFO):
        channel.send_alert(message, sample_log)

    assert "SIMULATING SENDING EMAIL" in caplog.text
    assert f"To: {recipient}" in caplog.text
    assert f"Subject: Fraud Alert Detected: Transaction {sample_log['tx_id']}" in caplog.text
    assert message in caplog.text
    assert f"User ID: {sample_log['user_id']}" in caplog.text
    assert f"Amount: {sample_log['amount']}" in caplog.text

def test_ivr_channel_simulation(caplog, sample_log):
    """Test if the simulated IVR call log output contains expected information."""
    service_num = "+1987654321"
    channel = IVRNotificationChannel(ivr_service_number=service_num)
    message = "Please verify."
    with caplog.at_level(logging.INFO):
        channel.send_alert(message, sample_log)

    assert "SIMULATING INITIATING IVR CALL" in caplog.text
    assert f"Calling User: {sample_log['phone']}" in caplog.text
    assert f"from {service_num}" in caplog.text
    assert message in caplog.text
    assert f"user {sample_log['user_id']}" in caplog.text
    assert f"amount: {sample_log['amount']}" in caplog.text

def test_ivr_channel_no_phone(caplog, sample_log):
    """Test IVR channel behavior when log entry has no phone number."""
    log_no_phone = sample_log.copy()
    log_no_phone["phone"] = None # Ensure phone is None or missing
    channel = IVRNotificationChannel()
    with caplog.at_level(logging.WARNING):
        channel.send_alert("Test message", log_no_phone)

    assert "SIMULATING INITIATING IVR CALL" not in caplog.text
    assert f"No phone number found for user {log_no_phone['user_id']}" in caplog.text

def test_email_init_invalid_email():
    """Test Email channel raises error on invalid email init."""
    with pytest.raises(ValueError, match="Invalid recipient email format"):
        EmailNotificationChannel("")
    with pytest.raises(ValueError, match="Invalid recipient email format"):
        EmailNotificationChannel("plainaddress")

# --- Test Vertex AI Detector Initialization (if available) ---
@pytest.mark.skipif(not VERTEX_AI_AVAILABLE, reason="google-cloud-aiplatform not installed or import failed")
def test_vertex_ai_detector_init_missing_params():
    """Test Vertex AI detector raises ValueError if params are missing."""
    with pytest.raises(ValueError, match="Project ID and Vertex AI Endpoint ID are required"):
        VertexAIDetector(project="", endpoint_id="test-ep")
    with pytest.raises(ValueError, match="Project ID and Vertex AI Endpoint ID are required"):
        VertexAIDetector(project="test-proj", endpoint_id="")

# Add more tests for VertexAIDetector is_anomaly method using mocking if needed
# This would involve mocking the aiplatform.Endpoint and its predict method.