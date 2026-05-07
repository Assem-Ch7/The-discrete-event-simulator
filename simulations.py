import os
import math
import random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from engine import Main

LAMBDAS   = [4, 6, 8, 12]     # arrival rates to test
MU        = 8                  # service rate per server
SIM_TIME  = 30.0              # seconds per run (long enough for steady-state, fast enough to run)
N_RUNS    = 10                 # independent replications for CI
Z95       = 1.96               # z-score for 95 % confidence interval
PLOT_DIR  = os.path.join(os.path.dirname(__file__), "plots")

os.makedirs(PLOT_DIR, exist_ok=True)


def mean_ci(samples):
    """Return (mean, half-width of 95 % CI) for a list of samples."""
    n    = len(samples)
    if n == 0:
        return 0.0, 0.0
    mu   = np.mean(samples)
    if n == 1:
        return float(mu), 0.0
    se   = np.std(samples, ddof=1) / math.sqrt(n)
    return float(mu), Z95 * float(se)


def run_scenario(label, num_servers, queue_capacity, lambdas=LAMBDAS,
                 mu=MU, sim_time=SIM_TIME, n_runs=N_RUNS):
    """
    Run n_runs replications for each lambda value.

    Returns a dict keyed by metric name, each value being a list of
    (mean, ci_half) tuples — one per lambda value.
    """
    print(f"\n{'='*60}")
    print(f"  Scenario : {label}")
    print(f"  Servers  : {num_servers}   Queue cap : {queue_capacity}   Runs : {n_runs}")
    print(f"{'='*60}")

    metric_keys = ["avg_n_system", "avg_n_queue",
                   "avg_wait", "drop_rate"]

    results = {k: [] for k in metric_keys}

    for lam in lambdas:
        per_run = {k: [] for k in metric_keys}

        for run in range(n_runs):
            # Fix a different seed per run so replications are independent
            random.seed(run * 1000 + int(lam * 10))

            m = Main.Run(
                n_clients     = 1,
                lambda_rate   = lam,
                mu            = mu,
                num_servers   = num_servers,
                queue_capacity= queue_capacity,
                sim_time      = sim_time,
                verbose       = False,
            )

            total_sent = m.get_total_arrivals() + m.get_total_drops()

            per_run["avg_n_system"].append(m.get_avg_n_system())
            per_run["avg_n_queue" ].append(m.get_avg_n_queue())
            per_run["avg_wait"    ].append(m.get_avg_wait_time())
            per_run["drop_rate"   ].append(
                m.get_total_drops() / total_sent if total_sent > 0 else 0.0)

        # Summarise across runs
        rho = lam / (num_servers * mu)
        print(f"\n  lambda={lam:2d}  rho={rho:.3f}")
        print(f"  {'Metric':<22} {'Mean':>10}  {'±95% CI':>10}")
        print(f"  {'-'*44}")
        for k in metric_keys:
            mu_val, ci = mean_ci(per_run[k])
            results[k].append((mu_val, ci))
            print(f"  {k:<22} {mu_val:>10.4f}  {ci:>10.4f}")

    return results


# ── Plotting ──────────────────────────────────────────────────────────────────

def plot_metric(scenarios, metric_key, ylabel, title, filename,
                lambdas=LAMBDAS, include_drops=False):
    """
    One figure, one subplot per scenario.
    Each subplot: x-axis = lambda, y-axis = metric mean, error bars = 95 % CI.
    """
    n_scenarios = len(scenarios)
    fig, axes   = plt.subplots(1, n_scenarios,
                               figsize=(5 * n_scenarios, 4),
                               sharey=False)
    if n_scenarios == 1:
        axes = [axes]

    for ax, (label, results) in zip(axes, scenarios.items()):
        means = [v[0] for v in results[metric_key]]
        cis   = [v[1] for v in results[metric_key]]

        ax.errorbar(lambdas, means, yerr=cis,
                    fmt="o-", capsize=5, color="#c62828",
                    ecolor="#666666", linewidth=2, markersize=6)
        ax.set_title(label, fontsize=11, fontweight="bold")
        ax.set_xlabel("Arrival rate λ (msgs/sec)", fontsize=9)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_xticks(lambdas)
        ax.grid(True, linestyle="--", alpha=0.5)

    fig.suptitle(title, fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    path = os.path.join(PLOT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  [PLOT SAVED] {path}")


def plot_all(scenarios):
    """Generate one PNG per metric across all four scenarios."""

    plot_metric(scenarios,
                metric_key = "avg_n_system",
                ylabel     = "E[N] — avg msgs in system",
                title      = "Average number in system (E[N])",
                filename   = "EN_system.png")

    plot_metric(scenarios,
                metric_key = "avg_n_queue",
                ylabel     = "E[Nq] — avg msgs in queue",
                title      = "Average number in queue (E[Nq])",
                filename   = "EN_queue.png")

    plot_metric(scenarios,
                metric_key = "avg_wait",
                ylabel     = "E[W] — avg wait time (s)",
                title      = "Average waiting time in queue (E[W])",
                filename   = "EW_wait.png")

    # Drop rate only meaningful for finite-capacity models
    finite_scenarios = {k: v for k, v in scenarios.items()
                        if "M/M/1/4" in k or "M/M/1/8" in k or "M/M/3/8" in k}
    if finite_scenarios:
        plot_metric(finite_scenarios,
                    metric_key = "drop_rate",
                    ylabel     = "Drop rate (fraction)",
                    title      = "Message drop rate (finite-capacity queues)",
                    filename   = "drop_rate.png")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "#"*60)
    print("#  Discrete-Event Simulator — Queue Model Experiments")
    print("#"*60)

    # ── M/M/1 : 1 server, infinite queue ─────────────────────────────────────
    r_mm1 = run_scenario(
        label         = "M/M/1",
        num_servers   = 1,
        queue_capacity= float("inf"),
    )

    # ── M/M/1/4 : 1 server, system capacity = 4 ──────────────────────────────
    # queue_capacity here means the waiting-room size; 1 server occupies 1 slot,
    # so total system capacity = queue_capacity + num_servers = 3 + 1 = 4.
    r_mm14 = run_scenario(
        label         = "M/M/1/4",
        num_servers   = 1,
        queue_capacity= 3,        # 3 waiting + 1 in service = K=4
    )

    # ── M/M/1/8 : 1 server, system capacity = 8 ──────────────────────────────
    r_mm18 = run_scenario(
        label         = "M/M/1/8",
        num_servers   = 1,
        queue_capacity= 7,        # 7 waiting + 1 in service = K=8
    )

    # ── M/M/3/8 : 3 servers, system capacity = 8 ─────────────────────────────
    r_mm38 = run_scenario(
        label         = "M/M/3/8",
        num_servers   = 3,
        queue_capacity= 5,        # 5 waiting + 3 in service = K=8
    )

    # ── Collect all scenarios for plotting ────────────────────────────────────
    scenarios = {
        "M/M/1"   : r_mm1,
        "M/M/1/4" : r_mm14,
        "M/M/1/8" : r_mm18,
        "M/M/3/8" : r_mm38,
    }

    print("\n\nGenerating plots …")
    plot_all(scenarios)

    print("\n" + "#"*60)
    print("#  All simulations complete.")
    print(f"#  Plots saved to: {PLOT_DIR}")
    print("#"*60 + "\n")


if __name__ == "__main__":
    main()
