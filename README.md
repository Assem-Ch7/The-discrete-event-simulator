# The-discrete-event-simulator

# Discrete-Event Simulator — Session 1 (Foundations)

Welcome to the `session1` branch of the Discrete-Event Simulator. This branch contains the foundational building blocks of our Next-Event Time Advance simulation engine.

## 🌿 Repository Structure (Branch Guide)
This repository is organized into three distinct branches to reflect the chronological progression of the lab assignments:
* **`session1` (Current)**: Focuses on the core architecture. It implements the basic event loop, priority scheduler, and primary network entities.
* **`session2`**: Introduces advanced queueing logic, including finite-capacity queues (packet dropping) and multi-server gateways.
* **`session3`**: Contains the final experimental framework, automated batch testing, statistical metrics (95% CIs), and plot generation.

## ⚙️ Core Components
This branch establishes the base classes required to simulate network traffic and server processing:
* **`scheduler.py`**: A Min-Heap (`heapq`) based event calendar that drives the simulation clock forward.
* **`event.py` & `message.py`**: Defines the data payloads and the timeline triggers (`SEND`, `RECV`, `DEPT`).
* **`client.py`**: Generates incoming traffic using a Poisson process (exponential inter-arrival times via $\lambda$).
* **`server.py`**: Simulates message processing delays using exponential service times ($\mu$).
* **`engine.py`**: The main execution loop linking the entities together.

## 🚀 How to Run
To run the basic smoke tests and verify the integrity of the base classes, execute:
```bash
python3 engine.py
```
