from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple
import csv, json, math
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class Vehicle:
    vid: str
    lane: str
    s: float
    v: float
    a: float = 0.0
    rho: float = 0.7
    p_coop: float = 0.5
    trust: float = 1.0
    v_min: float = 0.0
    v_max: float = 20.0
    a_min: float = -3.0
    a_max: float = 2.0
    initial_s: float = field(init=False)
    initial_v: float = field(init=False)

    def __post_init__(self) -> None:
        self.initial_s = float(self.s)
        self.initial_v = float(self.v)


@dataclass
class MergeParams:
    merge_s: float = 0.0
    sigma_t: float = 2.0
    evolve_dt: float = 0.12
    evolve_steps: int = 80
    safe_gap_cross: float = 2.0
    safe_gap_same: float = 1.0
    alpha_coop: float = 0.8
    beta_rationality: float = 1.0
    p_min: float = 0.05
    p_max: float = 0.95
    sim_dt: float = 0.1
    lowpass: float = 0.35
    kv: float = 0.8
    ka: float = 0.35


def free_arrival_time(vehicle: Vehicle, merge_s: float, eps: float = 1e-3) -> float:
    return max(0.0, merge_s - vehicle.s) / max(vehicle.v, eps)


def conflict_risk(vi: Vehicle, vj: Vehicle, params: MergeParams) -> float:
    if vi.lane == vj.lane:
        return 0.0
    ti = free_arrival_time(vi, params.merge_s)
    tj = free_arrival_time(vj, params.merge_s)
    return float(math.exp(-abs(ti - tj) / max(params.sigma_t, 1e-6)))


def payoff_matrix(risk: float) -> Tuple[float, float, float, float]:
    R = 2.0 + 1.2 * risk
    S = -0.6 - 0.4 * risk
    T = 2.6 - 0.5 * risk
    P = 0.6 - 4.5 * risk
    return R, S, T, P


def evolve_cooperation_probabilities(
    vehicles: List[Vehicle], params: MergeParams
) -> Dict[str, np.ndarray]:
    history = {v.vid: [v.p_coop] for v in vehicles}
    for _ in range(params.evolve_steps):
        old_p = {v.vid: v.p_coop for v in vehicles}
        new_p = {}
        for vi in vehicles:
            u_c = u_d = weight_sum = 0.0
            for vj in vehicles:
                if vi.vid == vj.vid or vi.lane == vj.lane:
                    continue
                risk = conflict_risk(vi, vj, params)
                if risk < 1e-4:
                    continue
                R, S, T, P = payoff_matrix(risk)
                pj = old_p[vj.vid]
                weight = np.clip(vi.trust, 0.0, 1.0) * risk
                u_c += weight * (pj * R + (1 - pj) * S)
                u_d += weight * (pj * T + (1 - pj) * P)
                weight_sum += weight
            if weight_sum > 0:
                u_c /= weight_sum
                u_d /= weight_sum
            p = old_p[vi.vid]
            dp = params.evolve_dt * vi.rho * p * (1-p) * (u_c-u_d)
            new_p[vi.vid] = float(np.clip(p + dp, params.p_min, params.p_max))
        for v in vehicles:
            v.p_coop = new_p[v.vid]
            history[v.vid].append(v.p_coop)
    return {k: np.asarray(v) for k, v in history.items()}


def priority(vehicle: Vehicle, params: MergeParams) -> float:
    t0 = free_arrival_time(vehicle, params.merge_s)
    return -t0 + params.alpha_coop * (1 - vehicle.p_coop) + params.beta_rationality * vehicle.rho


def build_merge_schedule(
    vehicles: List[Vehicle], params: MergeParams
) -> Tuple[List[str], Dict[str, float]]:
    queues: Dict[str, List[Vehicle]] = {}
    for v in vehicles:
        queues.setdefault(v.lane, []).append(v)
    for lane in queues:
        queues[lane].sort(key=lambda x: free_arrival_time(x, params.merge_s))

    schedule = []
    while any(queues.values()):
        heads = [q[0] for q in queues.values() if q]
        chosen = max(heads, key=lambda x: priority(x, params))
        schedule.append(chosen)
        queues[chosen.lane].pop(0)

    target_time = {}
    for k, v in enumerate(schedule):
        t0 = free_arrival_time(v, params.merge_s)
        if k == 0:
            target_time[v.vid] = t0
        else:
            prev = schedule[k-1]
            gap = params.safe_gap_same if prev.lane == v.lane else params.safe_gap_cross
            target_time[v.vid] = max(t0, target_time[prev.vid] + gap)
    return [v.vid for v in schedule], target_time


def plan_trajectories(
    vehicles: List[Vehicle], target_time: Dict[str, float], params: MergeParams
) -> Dict[str, Dict[str, np.ndarray]]:
    trajectories = {}
    horizon = max(target_time.values()) + 2.5
    n_steps = int(math.ceil(horizon / params.sim_dt)) + 1

    for veh in vehicles:
        s, v, a = veh.initial_s, veh.initial_v, veh.a
        ts, ss, vs, aas = [0.0], [s], [v], [a]
        crossed = False
        for k in range(1, n_steps):
            t = k * params.sim_dt
            if crossed:
                a_cmd = 0.0
            else:
                remain_t = max(target_time[veh.vid] - ts[-1], params.sim_dt)
                distance = max(0.0, params.merge_s - s)
                desired_avg_v = np.clip(distance / remain_t, veh.v_min, veh.v_max)
                a_arrival = 2 * (distance - v * remain_t) / max(remain_t**2, 1e-6)
                raw_a = params.kv * (desired_avg_v - v) + params.ka * a_arrival
                raw_a = np.clip(raw_a, veh.a_min, veh.a_max)
                a_cmd = (1 - params.lowpass) * a + params.lowpass * raw_a

            v = float(np.clip(v + a_cmd * params.sim_dt, veh.v_min, veh.v_max))
            s = s + v * params.sim_dt + 0.5 * a_cmd * params.sim_dt**2
            a = float(a_cmd)
            if s >= params.merge_s:
                crossed = True

            ts.append(t); ss.append(s); vs.append(v); aas.append(a)
            if crossed and t >= target_time[veh.vid] + 0.5:
                break

        trajectories[veh.vid] = {
            "t": np.asarray(ts), "s": np.asarray(ss),
            "v": np.asarray(vs), "a": np.asarray(aas)
        }
    return trajectories


def evaluate(
    vehicles: List[Vehicle], order: List[str], target_time: Dict[str, float], params: MergeParams
) -> Dict[str, float]:
    by_id = {v.vid: v for v in vehicles}
    delays = [target_time[v.vid] - free_arrival_time(v, params.merge_s) for v in vehicles]
    cross_gaps = []
    for a, b in zip(order[:-1], order[1:]):
        if by_id[a].lane != by_id[b].lane:
            cross_gaps.append(target_time[b] - target_time[a])
    return {
        "mean_delay_s": float(np.mean(delays)),
        "max_delay_s": float(np.max(delays)),
        "min_cross_lane_gap_s": float(np.min(cross_gaps)) if cross_gaps else float("inf"),
    }


def fixed_mainline_priority_schedule(vehicles: List[Vehicle], params: MergeParams) -> Dict[str, float]:
    main = sorted([v for v in vehicles if v.lane == "main"], key=lambda x: free_arrival_time(x, params.merge_s))
    ramp = sorted([v for v in vehicles if v.lane != "main"], key=lambda x: free_arrival_time(x, params.merge_s))
    order = main + ramp
    times = {}
    for i, v in enumerate(order):
        t0 = free_arrival_time(v, params.merge_s)
        if i == 0:
            times[v.vid] = t0
        else:
            prev = order[i-1]
            gap = params.safe_gap_same if prev.lane == v.lane else params.safe_gap_cross
            times[v.vid] = max(t0, times[prev.vid] + gap)
    return times


def save_outputs(vehicles, history, order, target_time, trajs, metrics, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    by_id = {v.vid: v for v in vehicles}

    with (outdir / "merge_schedule.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["order", "vehicle_id", "lane", "p_coop", "target_time_s"])
        for i, vid in enumerate(order, 1):
            v = by_id[vid]
            w.writerow([i, vid, v.lane, f"{v.p_coop:.4f}", f"{target_time[vid]:.4f}"])

    serializable = {k: (None if math.isinf(v) else v) for k, v in metrics.items()}
    (outdir / "metrics.json").write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")

    fig = plt.figure(figsize=(8, 5))
    for vid, seq in history.items():
        plt.plot(np.arange(len(seq)), seq, label=vid)
    plt.xlabel("Evolution step"); plt.ylabel("Cooperation probability"); plt.ylim(0, 1)
    plt.grid(alpha=0.25); plt.legend(ncol=2); plt.tight_layout()
    fig.savefig(outdir / "cooperation_evolution.png", dpi=160); plt.close(fig)

    fig = plt.figure(figsize=(8, 5))
    for vid in order:
        tr = trajs[vid]
        plt.plot(tr["t"], tr["s"], label=vid)
    plt.axhline(0.0, linestyle="--", linewidth=1)
    plt.xlabel("Time / s"); plt.ylabel("Longitudinal position s / m")
    plt.grid(alpha=0.25); plt.legend(ncol=2); plt.tight_layout()
    fig.savefig(outdir / "merge_trajectories.png", dpi=160); plt.close(fig)

    fixed = fixed_mainline_priority_schedule(vehicles, MergeParams())
    evo_delays = [target_time[v.vid] - free_arrival_time(v, 0.0) for v in vehicles]
    fixed_delays = [fixed[v.vid] - free_arrival_time(v, 0.0) for v in vehicles]
    x = np.arange(len(vehicles))
    fig = plt.figure(figsize=(8, 5))
    plt.bar(x - 0.18, evo_delays, width=0.36, label="Evolutionary game")
    plt.bar(x + 0.18, fixed_delays, width=0.36, label="Fixed mainline priority")
    plt.xticks(x, [v.vid for v in vehicles]); plt.ylabel("Delay / s")
    plt.grid(axis="y", alpha=0.25); plt.legend(); plt.tight_layout()
    fig.savefig(outdir / "delay_comparison.png", dpi=160); plt.close(fig)


def demo_vehicles() -> List[Vehicle]:
    return [
        Vehicle("M1", "main", -55, 12.0, rho=0.90, p_coop=0.42, trust=0.90),
        Vehicle("M2", "main", -89, 11.4, rho=0.78, p_coop=0.50, trust=0.88),
        Vehicle("M3", "main", -124, 12.1, rho=0.82, p_coop=0.46, trust=0.90),
        Vehicle("R1", "ramp", -49, 10.4, rho=0.62, p_coop=0.60, trust=0.82),
        Vehicle("R2", "ramp", -83, 10.8, rho=0.55, p_coop=0.58, trust=0.80),
        Vehicle("R3", "ramp", -119, 10.7, rho=0.70, p_coop=0.52, trust=0.85),
    ]


def main() -> None:
    params = MergeParams()
    vehicles = demo_vehicles()
    history = evolve_cooperation_probabilities(vehicles, params)
    order, target_time = build_merge_schedule(vehicles, params)
    trajs = plan_trajectories(vehicles, target_time, params)
    metrics = evaluate(vehicles, order, target_time, params)

    print("Merge order:", " -> ".join(order))
    for v in vehicles:
        print(f"{v.vid}: p={v.p_coop:.3f}, T0={free_arrival_time(v, 0):.2f}s, T*={target_time[v.vid]:.2f}s")
    print("Metrics:", metrics)

    save_outputs(vehicles, history, order, target_time, trajs, metrics, Path(__file__).resolve().parent / "outputs")


if __name__ == "__main__":
    main()
