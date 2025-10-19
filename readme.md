# Fraud Detection Simulation System
_Prepared by the student (MSc Cyber Security – University of Essex Online)._  

## 📁 Project Folder Structure Explained

| Path | Purpose | OOP Concept | Unit |
|------|---------|-------------|------|
| `src/interfaces.py` | Abstract contracts (LogSource, FraudDetector, NotificationChannel) | Abstraction, ISP | Unit 2–3 |
| `src/implementations.py` | Concrete classes for logs, detectors, channels | Inheritance, Encapsulation, Polymorphism | Unit 3–4 |
| `src/ai_detector.py` | AI-backed detector (Google Vertex AI) | LSP, Encapsulation, DI | Unit 5–6 |
| `src/services.py` | Service that composes and coordinates collaborators | DIP, Composition | Unit 6–7 |
| `main.py` | Composition Root: runtime wiring & configuration | IoC, Strategy selection | Unit 4–7 |
| `tests/` | Unit tests using mocks to verify DIP and SRP | Testability | Unit 8 |

## 🧩 OOP Principle References in Code (File + Line)
| File | Line | Principle | Unit | Description |
|------|------|-----------|------|-------------|
| `ai_detector.py` | 14 | Abstraction & LSP | Unit 5 | AI-based detector drop-in replacement. |
| `ai_detector.py` | 24 | Dependency Injection | Unit 6 | Constructor DI of AI client config. |
| `ai_detector.py` | 48 | Strategy via Interface | Unit 4 | Decision via common interface. |
| `implementations.py` | 32 | Inheritance & Encapsulation | Unit 3 | Concrete implementation of abstract source. |
| `implementations.py` | 57 | SRP & Encapsulation | Unit 4 | Detector encapsulates rule logic. |
| `implementations.py` | 96 | Polymorphism | Unit 3 | Email alert channel under common contract. |
| `implementations.py` | 120 | Polymorphism & Encapsulation | Unit 3 | IVR alert channel under common contract. |
| `interfaces.py` | 6 | Abstraction/ISP | Unit 2–3 | Abstract contracts enabling loose coupling. |
| `interfaces.py` | 18 | Abstraction/ISP | Unit 2–3 | Abstract contracts enabling loose coupling. |
| `interfaces.py` | 30 | Abstraction/ISP | Unit 2–3 | Abstract contracts enabling loose coupling. |
| `main.py` | 38 | Composition Root | Unit 7 | Runtime wiring of dependencies. |
| `main.py` | 86 | Strategy Selection | Unit 4 | Rule-based strategy selected. |
| `main.py` | 93 | OCP via Strategy | Unit 5 | Swap in AI strategy. |
| `services.py` | 9 | DI & DIP | Unit 6 | Constructor DI of abstract deps. |
| `services.py` | 25 | Orchestration | Unit 7 | Single method coordinates flow. |
| `test_implementations.py` | 122 | Test Constructor Validation | Unit 8 | Ensures invalid config raises. |
| `test_services.py` | 65 | Test for DIP | Unit 8 | Mocks confirm dependency inversion. |
| `test_services.py` | 90 | Test Polymorphism | Unit 8 | Ensures all channels receive alerts. |

## 🔄 High-Level Workflow

```
Transaction Logs  →  Fraud Detector  →  Notification Channels
        ↓                  ↓                     ↓
  [Simulated Data]   [Rule-Based / AI]   [Email / IVR Simulation]
```

## 🎯 Learning Outcomes Mapping (Essex AODP)

- **Design patterns**: Strategy via `FraudDetector` variants; Composition Root in `main.py`.
- **Secure & robust architecture**: Encapsulation, validation, error handling, environment-based config.
- **AI adaptability**: `VertexAIDetector` conforms to the same interface, enabling ML without refactoring callers.

---

##  Architecture Notes

Some instantiated components (e.g., `FraudMonitoringService`) may appear greyed out or marked as “unused” by IDEs such as VS Code.  
This is **intentional**. The architecture was designed with **future AI integration** in mind — for instance, replacing or extending the current rule-based `FraudDetector` with an AI-driven module (`VertexAIDetector`).  
Defining these components now ensures **extensibility** and compliance with the **Open/Closed Principle (OCP)** — the system is *open for extension, but closed for modification.*

> This anticipatory design allows smooth expansion toward real-time AI-driven fraud analysis without refactoring core logic.

---
