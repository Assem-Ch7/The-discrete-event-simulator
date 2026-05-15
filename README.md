# Discrete-Event Simulator — Session 2 (Advanced Queueing Models)

Welcome to the `session2` branch. Building upon the core engine from Session 1, this branch introduces complex routing, queue capacity limits, and statistical metric tracking.

## 🌿 Repository Structure (Branch Guide)
This repository is organized into three distinct branches to reflect the chronological progression of the lab assignments:
* **`session1`**: Focuses on the foundational architecture, event scheduling, and basic entities.
* **`session2` (Current)**: Focuses on advanced queueing variations (M/M/1, M/M/1/K, M/M/c/K) and time-weighted metric collection.
* **`session3`**: Contains the final experimental framework, automated batch testing, statistical metrics (95% CIs), and visual plot generation.

## 📈 Key Additions in this Branch
* **The Gateway (`gateway.py`)**: Acts as a load balancer and router. It checks for idle servers, manages the waiting room, and drops messages when the system hits capacity.
* **Finite Capacity (`queue.py`)**: Upgraded to support maximum size limits (K). If a message arrives when the queue is full, it is officially dropped.
* **Multi-Server Support**: The architecture now supports multiple identical parallel servers (c) to simulate higher-throughput network nodes.
* **Time-Weighted Metrics (`metrics.py`)**: Instead of simple step-averaging, this module calculates integrals over time ($\int N(t) dt$) to accurately compute $E[N]$ (expected number in system) and $E[N_q]$ (expected number in queue).

## 🚀 How to Run
To run an integrated simulation testing the Gateway logic, queue limits, and metric collection, execute:
```bash
python3 engine.py
```
