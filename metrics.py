# metrics.py
# Collects and summarises all simulation statistics required by the spec:
#   - Instant number of messages in the system and in the queue
#   - Total (cumulative) messages that entered / left the system
#   - Time-averaged number in system and queue  (Little's Law quantities)
#   - Per-message sojourn time (time in system) and waiting time (time in queue)
#   - Number of dropped messages (for finite-capacity queues)
#
# Design
# ------
# The engine calls advance_time(t) + sync_counts(n_sys, n_q) at the start of
# every event, BEFORE modifying state.  This accumulates the area under the
# N(t) step-function using the counts that were true during [t_prev, t].
# record_* methods track per-message timestamps for sojourn / wait times.


class Metrics:
    def __init__(self):
        # ── Time-averaging state ──────────────────────────────────────────────
        self._last_event_time    = 0.0   # time of last advance_time call
        self._area_system        = 0.0   # ∫ N_system(t) dt
        self._area_queue         = 0.0   # ∫ N_queue(t)  dt

        # ── Instant counters (synced from gateway each event) ─────────────────
        self._n_system           = 0
        self._n_queue            = 0

        # ── Totals ────────────────────────────────────────────────────────────
        self._total_arrivals     = 0     # messages accepted into the system
        self._total_departures   = 0     # messages that completed service
        self._total_drops        = 0     # messages rejected (queue full)

        # ── Per-message timestamps (keyed by message_id) ──────────────────────
        self._arrival_time       = {}    # msg_id -> time of RECV_MSG acceptance
        self._service_start_time = {}    # msg_id -> time server picked it up

        # ── Sojourn / wait accumulators ───────────────────────────────────────
        self._total_sojourn_time = 0.0   # Σ (departure_time - arrival_time)
        self._total_wait_time    = 0.0   # Σ (service_start  - arrival_time)

        # ── Final averages (set by finalise()) ───────────────────────────────
        self.avg_n_system        = 0.0
        self.avg_n_queue         = 0.0
        self.avg_sojourn_time    = 0.0
        self.avg_wait_time       = 0.0
        self.sim_time            = 0.0

    # ── Time-step accumulator ────────────────────────────────────────────────

    def advance_time(self, new_time):
        """
        Accumulate ∫N(t)dt for the interval [last_event_time, new_time]
        using the snapshot of _n_system / _n_queue from the PREVIOUS event.
        Call this at the very start of each event, before syncing counts.
        """
        dt = new_time - self._last_event_time
        if dt > 0:
            self._area_system += self._n_system * dt
            self._area_queue  += self._n_queue  * dt
        self._last_event_time = new_time

    def sync_counts(self, n_system, n_queue):
        """
        Overwrite the instant counters with the gateway's true state.
        Call this immediately AFTER advance_time, before processing the event.
        """
        self._n_system = n_system
        self._n_queue  = n_queue

    # ── Event-level record calls ─────────────────────────────────────────────

    def record_arrival(self, message, arrival_time: float):
        """
        Called when a RECV_MSG is accepted into the system (not dropped).
        Records the arrival timestamp for sojourn/wait accounting.
        """
        self._arrival_time[message.get_message_id()] = arrival_time
        self._total_arrivals += 1

    def record_service_start(self, message, service_start_time: float):
        """
        Called by Gateway._start_service when a message leaves the queue
        and enters a server.  Records the service-start time so we can
        compute the time the message spent waiting in the queue.
        """
        msg_id = message.get_message_id()
        self._service_start_time[msg_id] = service_start_time

        if msg_id in self._arrival_time:
            wait = service_start_time - self._arrival_time[msg_id]
            self._total_wait_time += max(wait, 0.0)

    def record_departure(self, message, departure_time: float):
        """
        Called when a DEPT_MSG fires — message has left the system entirely.
        Computes sojourn time.  If service_start was never recorded (message
        went straight to a free server so queue wait = 0), we handle it here.
        """
        msg_id = message.get_message_id()
        self._total_departures += 1

        if msg_id in self._arrival_time:
            sojourn = departure_time - self._arrival_time[msg_id]
            self._total_sojourn_time += max(sojourn, 0.0)

            # If service_start was never recorded it means the message bypassed
            # the queue entirely (server was free on arrival).  Wait time = 0,
            # so nothing extra to add to _total_wait_time.
            if msg_id not in self._service_start_time:
                self._service_start_time[msg_id] = self._arrival_time[msg_id]

    def record_drop(self):
        """Called when a message is rejected because the queue is full."""
        self._total_drops += 1

    # ── Finalise ─────────────────────────────────────────────────────────────

    def finalise(self, sim_time: float):
        """
        Flush remaining area up to sim_time and compute all averages.
        Call exactly once at the end of the simulation.
        """
        self.sim_time = sim_time
        self.advance_time(sim_time)          # flush last interval

        self.avg_n_system = (self._area_system / sim_time) if sim_time > 0 else 0.0
        self.avg_n_queue  = (self._area_queue  / sim_time) if sim_time > 0 else 0.0

        n = self._total_departures
        self.avg_sojourn_time = (self._total_sojourn_time / n) if n > 0 else 0.0
        self.avg_wait_time    = (self._total_wait_time    / n) if n > 0 else 0.0

    # ── Accessors ─────────────────────────────────────────────────────────────

    def get_instant_n_system(self):   return self._n_system
    def get_instant_n_queue(self):    return self._n_queue
    def get_total_arrivals(self):     return self._total_arrivals
    def get_total_departures(self):   return self._total_departures
    def get_total_drops(self):        return self._total_drops
    def get_avg_n_system(self):       return self.avg_n_system
    def get_avg_n_queue(self):        return self.avg_n_queue
    def get_avg_sojourn_time(self):   return self.avg_sojourn_time
    def get_avg_wait_time(self):      return self.avg_wait_time

    # ── Pretty-print ──────────────────────────────────────────────────────────

    def print_summary(self):
        print("\n" + "="*55)
        print("  SIMULATION METRICS SUMMARY")
        print("="*55)
        print(f"  Simulation time           : {self.sim_time:.1f} s")
        print(f"  Total arrivals            : {self._total_arrivals}")
        print(f"  Total departures          : {self._total_departures}")
        print(f"  Total drops               : {self._total_drops}")
        print("-"*55)
        print(f"  Instant N in system       : {self._n_system}")
        print(f"  Instant N in queue        : {self._n_queue}")
        print("-"*55)
        print(f"  Avg N in system  (E[N])   : {self.avg_n_system:.4f}")
        print(f"  Avg N in queue   (E[Nq])  : {self.avg_n_queue:.4f}")
        print(f"  Avg sojourn time (E[T])   : {self.avg_sojourn_time:.4f} s")
        print(f"  Avg waiting time (E[W])   : {self.avg_wait_time:.4f} s")
        print("="*55 + "\n")
