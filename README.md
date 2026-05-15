# Discrete-Event Simulator — NCA USEEJ7

## REQUIREMENTS
* Python 3.8+
* `pip install numpy matplotlib`

## RUN (default parameters)
```bash
python3 simulations.py
```
This setup runs all 4 scenarios (**M/M/1**, **M/M/1/4**, **M/M/1/8**, and **M/M/3/8**) using the following parameters:

* **Arrival Rates ($\lambda$):** 4, 6, 8, 12 msgs/sec
* **Service Rate ($\mu$):** 8 msgs/sec
* **Independent Runs:** 100 per scenario
* **Simulation Time:** 30 seconds per run
* **Client Sources:** 1

> **Note:** Generated plots are saved to the `plots/` subfolder.

### RUN (custom parameters)

```bash
  python3 simulations.py [OPTIONS]
```
**Options:**
* **`--lambdas <values>`:** Arrival rates to test (space-separated)
* **`--mu <value>`:** Service rate per server (msgs/sec)
* **`--sim-time <value>`:** Simulation duration per run (seconds)
* **`--n-runs <value>`:** Number of independent runs per scenario
* **`--n-clients <value>`:** Number of client sources

### Examples

```bash
  # Use a single lambda value and fewer runs (quick test)
  python3 simulations.py --lambdas 4 8 --n-runs 10

  # Change service rate and simulation time
  python3 simulations.py --mu 10 --sim-time 60

  # Full custom run
  python3 simulations.py --lambdas 2 4 6 8 10 --mu 12 --sim-time 50 --n-runs 100 --n-clients 2
```
### PROJECT STRUCTURE

* **`simulations.py`:** Entry point — runs all scenarios and generates plots
* **`engine.py`:** Simulation loop (Run, CreateClients, GenerateTrace, test methods)
* **`gateway.py`:** Message routing — receive_msg(), departure_msg()
* **`client.py`:** Message source — generates arrivals (exponential inter-arrival)
* **`server.py`:** Service node — exponential service times
* **`queue.py`:** FIFO waiting room with configurable capacity
* **`scheduler.py`:** Min-heap event queue
* **`event.py`:** Event class and EventType enum (SEND_MSG, RECV_MSG, MSG_DEPT)
* **`message.py`:** Message class
* **`metrics.py`:** Statistics collector ($E[N]$, $E[N_q]$, $E[W]$, $E[T]$, $E[S]$, drop rate)
* **`plots/`:** Output folder for generated PNG plots

```text
[Client] ──(SEND)──► [Propagation Delay (+1.0s)] ──(RECV)──► [Gateway]
                                                                 │
                                         ┌───────────────────────┴───────────────────────┐
                                         ▼                                               ▼
                                   [Server Free?]                                [All Servers Busy?]
                                         │                                               │
                                         ▼                                               ▼
                                  (Direct Service)                                 [Queue Full?]
                                         │                                     ┌─────────┴─────────┐
                                         ▼                                     ▼                   ▼
                                   Generate DEPT                           (ENQUEUE)             (DROP)
                                         │                                     │                   │
                                         ▼                                     ▼                   ▼
                                   Advance Clock                         Wait in Queue         Increments
                                                                               │               Drop Metric
                                                                               ▼
                                                                         Next DEPT pulls
                                                                         from Queue
                                                                               ▼



```
                                                                         Next DEPT pulls
                                                                         from Queue
