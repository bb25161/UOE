# File: tests/test_services.py

import pytest
import logging
from typing import Any, Callable, Generator
from pytest_mock import MockerFixture
from unittest.mock import call, MagicMock
from src.services import FraudMonitoringService
from src.interfaces import LogSource, FraudDetector, NotificationChannel



# Test depends on abstractions
from src.interfaces import LogSource, FraudDetector, NotificationChannel

# --- Test Data ---
SAMPLE_LOGS_VALID = [
    {"tx_id": "t001", "user_id": "u001", "amount": 100.0, "ip":"1.1.1.1"},
    {"tx_id": "t002", "user_id": "u002", "amount": 6000.0, "ip":"2.2.2.2"}, # Anomaly
    {"tx_id": "t003", "user_id": "u001", "amount": 50.0, "ip":"1.1.1.1"},
]
ANOMALOUS_LOG = SAMPLE_LOGS_VALID[1]
NORMAL_LOGS = [SAMPLE_LOGS_VALID[0], SAMPLE_LOGS_VALID[2]]
INVALID_LOG_MISSING_KEY = {"tx_id": "t-invalid", "user_id":"u-invalid"} # Missing 'amount'


# --- Pytest Fixtures using Mocks ---
# OOP Benefit: DI and Abstraction allow easy mocking for isolated testing.

@pytest.fixture
def mock_log_source(mocker: Callable[..., Generator[MockerFixture, None, None]]):
    """Fixture for a mocked LogSource."""
    mock = mocker.Mock(spec=LogSource)
    # Use MagicMock to allow iteration if needed, though get_logs returns a list directly
    mock.get_logs = MagicMock(return_value=SAMPLE_LOGS_VALID)
    return mock

@pytest.fixture
def mock_detector_anomaly(mocker: Callable[..., Generator[MockerFixture, None, None]]):
    """Fixture for a mocked FraudDetector that flags the anomalous log."""
    mock = mocker.Mock(spec=FraudDetector)
    # Return True only if the log matches the known anomalous one
    mock.is_anomaly.side_effect = lambda log: log["tx_id"] == ANOMALOUS_LOG["tx_id"]
    return mock

@pytest.fixture
def mock_detector_no_anomaly(mocker: Callable[..., Generator[MockerFixture, None, None]]):
    """Fixture for a mocked FraudDetector that never flags anything."""
    mock = mocker.Mock(spec=FraudDetector)
    mock.is_anomaly.return_value = False
    return mock

@pytest.fixture
def mock_notification_channels(mocker: Callable[..., Generator[MockerFixture, None, None]]):
    """Fixture for a list of mocked NotificationChannels."""
    channel1 = mocker.Mock(spec=NotificationChannel, name="MockEmailChannel")
    channel2 = mocker.Mock(spec=NotificationChannel, name="MockIVRChannel")
    # Make send_alert a MagicMock to track calls easily
    channel1.send_alert = MagicMock()
    channel2.send_alert = MagicMock()
    return [channel1, channel2]

# --- Tests for FraudMonitoringService ---

# Testing Focus: Verifies DIP via mocks; constructor injection accepts abstractions.
# Unit Reference: Unit 8 – Testing & Quality
def test_service_initialization_valid(mock_log_source: Any, mock_detector_no_anomaly: Any, mock_notification_channels: list):
    """Test successful initialization with valid mocked dependencies."""
    try:
        service = FraudMonitoringService(
            log_source=mock_log_source,
            detector=mock_detector_no_anomaly,
            channels=mock_notification_channels
        )
        assert isinstance(service, FraudMonitoringService)
    except (TypeError, ValueError) as e:
        pytest.fail(f"Initialization failed with valid mocks: {e}")

def test_service_initialization_invalid_dependencies(mock_log_source: Any, mock_detector_no_anomaly: Any, mock_notification_channels: list):
    """Test initialization raises TypeError with invalid dependencies types or empty channels."""
    with pytest.raises(TypeError, match="log_source must implement"):
        FraudMonitoringService(log_source="not a log source", detector=mock_detector_no_anomaly, channels=mock_notification_channels)
    with pytest.raises(TypeError, match="detector must implement"):
        FraudMonitoringService(log_source=mock_log_source, detector=None, channels=mock_notification_channels)
    with pytest.raises(TypeError, match="channels must be a non-empty list"): # Empty channel list
        FraudMonitoringService(log_source=mock_log_source, detector=mock_detector_no_anomaly, channels=[])
    with pytest.raises(TypeError, match="channels must be a non-empty list"): # List contains non-channel object
        FraudMonitoringService(log_source=mock_log_source, detector=mock_detector_no_anomaly, channels=[mock_notification_channels[0], "not a channel"])

# Testing Focus: Validates polymorphism (multiple channels) & orchestration flow.
# Unit Reference: Unit 8 – Testing & Quality
def test_monitor_and_alert_anomaly_detected_calls_detector_and_channels(mock_log_source: Any, mock_detector_anomaly: Any, mock_notification_channels: list):
    """Test alert sending logic when an anomaly is detected."""
    service = FraudMonitoringService(
        log_source=mock_log_source,
        detector=mock_detector_anomaly,
        channels=mock_notification_channels
    )
    service.monitor_and_alert()

    # Verify log source was called once
    mock_log_source.get_logs.assert_called_once()

    # Verify detector was called for each valid log entry
    assert mock_detector_anomaly.is_anomaly.call_count == len(SAMPLE_LOGS_VALID)
    calls = [call(SAMPLE_LOGS_VALID[0]), call(SAMPLE_LOGS_VALID[1]), call(SAMPLE_LOGS_VALID[2])]
    mock_detector_anomaly.is_anomaly.assert_has_calls(calls, any_order=False) # Check order if important

    # Verify send_alert was called on ALL channels ONLY for the anomalous log
    # OOP Principle: Polymorphism verified - send_alert called on different mock types.
    expected_message = f"Potential fraudulent activity detected for transaction {ANOMALOUS_LOG['tx_id']}."
    for channel in mock_notification_channels:
        channel.send_alert.assert_called_once_with(expected_message, ANOMALOUS_LOG)

def test_monitor_and_alert_no_anomaly_detected_does_not_alert(mock_log_source: Any, mock_detector_no_anomaly: Any, mock_notification_channels: list):
    """Test that no alerts are sent when no anomaly is detected."""
    service = FraudMonitoringService(
        log_source=mock_log_source,
        detector=mock_detector_no_anomaly,
        channels=mock_notification_channels
    )
    service.monitor_and_alert()

    # Verify detector was called for all logs
    assert mock_detector_no_anomaly.is_anomaly.call_count == len(SAMPLE_LOGS_VALID)

    # Verify send_alert was NEVER called on any channel
    for channel in mock_notification_channels:
        channel.send_alert.assert_not_called()

def test_monitor_and_alert_skips_invalid_log_entry(mock_log_source: Any, mock_detector_no_anomaly: Any, mock_notification_channels: list, caplog: pytest.LogCaptureFixture):
    """Test that logs missing required keys are skipped gracefully."""
    # Setup mock to return a mix of valid and invalid logs
    mixed_logs = [SAMPLE_LOGS_VALID[0], INVALID_LOG_MISSING_KEY, SAMPLE_LOGS_VALID[2]]
    mock_log_source.get_logs.return_value = mixed_logs

    service = FraudMonitoringService(
        log_source=mock_log_source,
        detector=mock_detector_no_anomaly,
        channels=mock_notification_channels
    )
    with caplog.at_level(logging.WARNING):
        service.monitor_and_alert()

    # Verify detector was called only for the VALID logs
    assert mock_detector_no_anomaly.is_anomaly.call_count == 2 # Only for valid logs
    mock_detector_no_anomaly.is_anomaly.assert_any_call(SAMPLE_LOGS_VALID[0])
    mock_detector_no_anomaly.is_anomaly.assert_any_call(SAMPLE_LOGS_VALID[2])

    # Verify no alerts were sent
    for channel in mock_notification_channels:
        channel.send_alert.assert_not_called()

    # Check that a warning was logged for the invalid entry
    assert "Skipping log entry due to missing required keys" in caplog.text

def test_monitor_and_alert_handles_detector_exception_gracefully(mock_log_source: Any, mock_detector_anomaly: Any, mock_notification_channels: list, caplog: pytest.LogCaptureFixture):
    """Test that an exception during detection doesn't stop processing other logs."""
    # Configure detector mock to raise an exception for the anomalous log
    detection_error_message = "Simulated Detection Error!"
    mock_detector_anomaly.is_anomaly.side_effect = lambda log: (_ for _ in ()).throw(Exception(detection_error_message)) if log["tx_id"] == ANOMALOUS_LOG["tx_id"] else False

    service = FraudMonitoringService(
        log_source=mock_log_source,
        detector=mock_detector_anomaly,
        channels=mock_notification_channels
    )
    with caplog.at_level(logging.ERROR):
        service.monitor_and_alert()

    # Verify detector was still called (or attempted) for all logs
    assert mock_detector_anomaly.is_anomaly.call_count == len(SAMPLE_LOGS_VALID)

    # Verify no alerts were sent because detection failed for the anomaly
    for channel in mock_notification_channels:
        channel.send_alert.assert_not_called()

    # Verify the detection error was logged
    assert detection_error_message in caplog.text
    assert f"Error during anomaly detection for tx {ANOMALOUS_LOG['tx_id']}" in caplog.text

def test_monitor_and_alert_handles_one_channel_failing(mock_log_source: Any, mock_detector_anomaly: Any, mock_notification_channels: list, caplog: pytest.LogCaptureFixture):
    """Test that if one notification channel fails, others are still attempted."""
    # Configure the first channel to raise an exception
    failing_channel = mock_notification_channels[0]
    working_channel = mock_notification_channels[1]
    notification_error_message = "Simulated SMTP Error!"
    failing_channel.send_alert.side_effect = Exception(notification_error_message)

    service = FraudMonitoringService(
        log_source=mock_log_source,
        detector=mock_detector_anomaly, # Will detect anomaly for ANOMALOUS_LOG
        channels=mock_notification_channels
    )
    with caplog.at_level(logging.ERROR):
        service.monitor_and_alert()

    # Verify send_alert was attempted on the failing channel (called once)
    failing_channel.send_alert.assert_called_once()

    # Verify send_alert WAS successfully called on the working channel
    expected_message = f"Potential fraudulent activity detected for transaction {ANOMALOUS_LOG['tx_id']}."
    working_channel.send_alert.assert_called_once_with(expected_message, ANOMALOUS_LOG)

    # Verify the notification error was logged
    assert notification_error_message in caplog.text
    assert f"Error sending alert via {failing_channel.name}" in caplog.text # Using mock name

def test_monitor_handles_log_source_exception(mock_log_source: Any, mock_detector_no_anomaly: Any, mock_notification_channels: list, caplog: pytest.LogCaptureFixture):
    """Test that if fetching logs fails, the error is logged and no detection/alerting happens."""
    log_source_error_message = "Simulated connection error to log source!"
    mock_log_source.get_logs.side_effect = Exception(log_source_error_message)

    service = FraudMonitoringService(
        log_source=mock_log_source,
        detector=mock_detector_no_anomaly,
        channels=mock_notification_channels
    )
    with caplog.at_level(logging.ERROR):
        service.monitor_and_alert()

    # Verify get_logs was called
    mock_log_source.get_logs.assert_called_once()

    # Verify detector was NOT called
    mock_detector_no_anomaly.is_anomaly.assert_not_called()

    # Verify no alerts were sent
    for channel in mock_notification_channels:
        channel.send_alert.assert_not_called()

    # Verify the source error was logged
    assert log_source_error_message in caplog.text
    assert "Critical error fetching logs from source" in caplog.text