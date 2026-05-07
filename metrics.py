class Metrics:
    def __init__(self):
        self._last_event_time = 0.0
        self._area_system     = 0.0
        self._area_queue      = 0.0

        self._n_system        = 0
        self._n_queue         = 0

        self._total_arrivals  = 0
        self._total_drops     = 0

        self.avg_n_system     = 0.0
        self.avg_n_queue      = 0.0
        self.avg_wait_time    = 0.0
        self.sim_time         = 0.0

    def advance_time(self, new_time):
        """Accumulate ∫N(t)dt for the interval since the last event."""
        dt = new_time - self._last_event_time
        if dt > 0:
            self._area_system += self._n_system * dt
            self._area_queue  += self._n_queue  * dt
        self._last_event_time = new_time

    def sync_counts(self, n_system, n_queue):
        """Update instant counters from the gateway's current state."""
        self._n_system = n_system
        self._n_queue  = n_queue

    def record_arrival(self):
        """Called when a message is accepted into the system."""
        self._total_arrivals += 1

    def record_drop(self):
        """Called when a message is rejected because the queue is full."""
        self._total_drops += 1

    def finalise(self, sim_time):
        """Compute all averages at the end of the simulation."""
        self.sim_time = sim_time
        self.advance_time(sim_time)

        self.avg_n_system = self._area_system / sim_time if sim_time > 0 else 0.0
        self.avg_n_queue  = self._area_queue  / sim_time if sim_time > 0 else 0.0

        lam = self._total_arrivals / sim_time if sim_time > 0 else 0.0
        self.avg_wait_time = self.avg_n_queue / lam if lam > 0 else 0.0

    def get_instant_n_system(self):  return self._n_system
    def get_instant_n_queue(self):   return self._n_queue
    def get_total_arrivals(self):    return self._total_arrivals
    def get_total_drops(self):       return self._total_drops
    def get_avg_n_system(self):      return self.avg_n_system
    def get_avg_n_queue(self):       return self.avg_n_queue
    def get_avg_wait_time(self):     return self.avg_wait_time

    def print_summary(self):
        print("\n" + "="*55)
        print("  SIMULATION METRICS SUMMARY")
        print("="*55)
        print(f"  Simulation time           : {self.sim_time:.1f} s")
        print(f"  Total arrivals            : {self._total_arrivals}")
        print(f"  Total drops               : {self._total_drops}")
        print("-"*55)
        print(f"  Instant N in system       : {self._n_system}")
        print(f"  Instant N in queue        : {self._n_queue}")
        print("-"*55)
        print(f"  Avg N in system  (E[N])   : {self.avg_n_system:.4f}")
        print(f"  Avg N in queue   (E[Nq])  : {self.avg_n_queue:.4f}")
        print(f"  Avg waiting time (E[W])   : {self.avg_wait_time:.4f} s")
        print("="*55 + "\n")
