# UOE
University of Essex Object Oriented Programing# Fraud Detection Capstone Project - UOE

This project is a Capstone project demonstration for the **University of Essex Online - Advanced Object-Oriented Design and Programming** module. It simulates a fraud detection system that processes mobile transaction logs, identifies potential anomalies, and triggers alerts.

## Project Overview

The system is designed to:
1.  **Fetch** transaction logs from a defined source.
2.  **Analyze** each log entry using a configurable fraud detection strategy.
3.  **Trigger alerts** through one or more notification channels (e.g., Email, IVR) if an anomaly is detected.

The core design emphasizes Object-Oriented Programming (OOP) principles and secure software development practices:

-   **Abstraction:** Interfaces (`LogSource`, `FraudDetector`, `NotificationChannel`) define contracts for components.
-   **Encapsulation:** Internal state and logic (e.g., detection thresholds, recipient details) are hidden within classes.
-   **Polymorphism:** Different notification channels and detection strategies can be used interchangeably through common interfaces.
-   **SOLID Principles:**
    -   *Single Responsibility Principle (SRP):* Classes have focused responsibilities.
    -   *Open/Closed Principle (OCP):* New detectors or channels can be added without modifying the core `FraudMonitoringService`.
    -   *Liskov Substitution Principle (LSP):* Different detector/channel implementations can substitute their base interfaces.
    -   *Dependency Inversion Principle (DIP):* The core service depends on abstractions, not concrete implementations.
-   **Dependency Injection (DI):** Dependencies are injected into the `FraudMonitoringService` (via constructor), promoting loose coupling and high testability.
-   **Adaptability for AI:** The design allows swapping the rule-based detector with an AI-based implementation (like the included `VertexAIDetector`) by changing the configuration, demonstrating adaptability for AI models.
-   **Security Considerations:** Input validation placeholders, secure configuration principles (using environment variables), and error handling are incorporated.

## Project Structure
