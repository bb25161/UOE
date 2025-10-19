# 🎓 Fraud Detection Simulation System
### University of Essex Online – Advanced Object-Oriented Design & Programming

---

**Capstone Project | MSc Cyber Security Program**  
Designed & Developed by **bb25161**

---

## 💡 Overview

This project is a **simulation-based fraud detection system** developed as part of the *Advanced Object-Oriented Design and Programming* module at the **University of Essex Online**.  
It demonstrates how modern **Object-Oriented Programming (OOP)** principles and **secure software design** can be applied to build a modular, maintainable, and testable system.

The system:

- Fetches **simulated mobile transaction logs**
- Detects **anomalies or potential fraud**
- Sends **simulated alerts** via Email and IVR
- Can be easily **extended with AI-based detection models** in the future

>  *This simulation uses synthetic logs to mimic real-world fraud behavior. The architecture, however, is fully adaptable for real data streams or AI-based analysis.*

---

##  Architectural Overview

![Architecture Diagram](docs/architecture_diagram.svg)

**Data Flow:**

```
Transaction Logs  →  Fraud Detector  →  Notification Channels
        ↓                  ↓                     ↓
  [Simulated Data]   [Rule-Based / AI]   [Email / IVR Simulation]
```

Each component is independently replaceable — promoting **loose coupling**, **encapsulation**, and **testability**.

---

## ⚙️ System Components

| Layer | Class / Module | Description | Key OOP Principle |
|-------|----------------|-------------|-------------------|
| **Data Layer** | `SimpleListLogSource` | Generates mock log data for simulation | Abstraction |
| **Detection Layer** | `SimpleRuleBasedDetector` | Detects anomalies exceeding defined thresholds | Encapsulation |
|  | `VertexAIDetector` | Placeholder for future AI integration (Google Vertex AI) | Open/Closed Principle |
| **Notification Layer** | `EmailNotificationChannel`, `IVRNotificationChannel` | Simulates sending alerts via email & IVR | Polymorphism |
| **Core Service** | `FraudMonitoringService` | Coordinates end-to-end fraud monitoring | Dependency Inversion |
| **Interface Layer** | `LogSource`, `FraudDetector`, `NotificationChannel` | Defines abstraction contracts | Abstraction & LSP |

---

## 🏗️ OOP Principles in Action

| Principle | Applied In | Implementation |
|------------|-------------|----------------|
| **Abstraction** | `interfaces.py` | Abstract base classes define component contracts. |
| **Encapsulation** | `implementations.py` | Internal logic (e.g., thresholds) hidden inside classes. |
| **Inheritance** | `VertexAIDetector` | Extends base detector to support AI models. |
| **Polymorphism** | `EmailNotificationChannel`, `IVRNotificationChannel` | Same interface, different behavior. |
| **SOLID Principles** | All modules | SRP, OCP, LSP, and DIP consistently applied. |
| **Dependency Injection (DI)** | `FraudMonitoringService` | Dependencies are injected through constructors. |

---

## 🔄 System Workflow


flowchart TD
    A[Fetch Transaction Logs] --> B[Analyze Entries via FraudDetector]
    B -->|Normal| C[No Action Required]
    B -->|Anomaly Detected| D[Trigger Notifications]
    D --> E[Email Alert]
    D --> F[IVR Call Simulation]
    E --> G[Summarize Results]
    F --> G
    G --> H[Generate Log Report + Summary]
```

---

##  Learning Outcomes

- ✅ Applying **Object-Oriented Programming** in a real-world simulation.  
- ✅ Designing a **modular, testable architecture** with dependency injection.  
- ✅ Implementing **secure-by-design** principles aligned with **NIST SSDF**.  
- ✅ Simulating detection and alert mechanisms using **Python logging**.  
- ✅ Understanding **polymorphism and interface-driven design**.  
- ✅ Building an architecture ready for **AI integration**.  

---

## 🔐 Security-by-Design Features

- Configuration via environment variables (`.env`) for secure settings.  
- Structured **logging** and **error handling** for traceability.  
- Encapsulation of thresholds and credentials.  
- **Input validation** placeholders for real-world data sources.  
- Designed following **NIST SP 800-218 (SSDF)** principles.  

---

## 🧰 Technologies Used

| Category | Technology |
|-----------|-------------|
| Language | Python 3.10+ |
| Paradigm | Object-Oriented Programming |
| Libraries | `logging`, `abc`, `colorama`, `pytest`, `dataclasses` |
| Architecture | Modular, layered design |
| AI Integration | Google Vertex AI (future) |
| Secure Config | `.env` environment variables |
| Documentation | Markdown + Mermaid + UML-style diagrams |

---

## 📊 Example Output

```
💡 Fraud Detection Simulation System (University of Essex)
------------------------------------------------------------
🔍 Fetching logs...
⚙️  Running fraud detection rules...
⚠️  ANOMALY: Tx ID t1002 | Amount: 5500.0 | User: u02
📧 Email sent to alert-team@example.com
📞 IVR call simulated: Fraud alert for Tx ID t1002
============================================================
📊 Fraud Detection Summary
------------------------------------------------------------
Total logs processed   : 5
Detected anomalies     : 2
Detection duration     : 1.503 seconds
============================================================
✅ Fraud monitoring cycle completed.
```

---

## 🚀 Future Enhancements

- Integration with **real transaction APIs**.  
- **AI/ML-based anomaly scoring** using Vertex AI.  
- Real-time **visual dashboards** (Flask/FastAPI).  
- Microservices scalability for fintech environments.  
- Cloud-based alerting integrations (Twilio, AWS SNS, GCP Pub/Sub).  

---

 
*MSc Cyber Security – University of Essex Online*  


---

