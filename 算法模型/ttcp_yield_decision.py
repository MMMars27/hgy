from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import csv
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class Vehicle:
    vid: str
    distance_to_conflict: float
    speed: float
    road_priority: float


@dataclass
class TTCPParams:
    safe_gap: float = 1.2
    v_min: float = 0.1
    v_max: float = 15.0
    a_min: float = -3.0
    a_max: float = 2.0
    w_t: float = 0.55
    w_v: float = 0.25
    w_r: float = 0.20
    dt: float = 0.1


def compute_ttcp(vehicle: Vehicle, eps: float = 1e-3) -> float:
    return max(0.0, vehicle.distance_to_conflict) / max(vehicle.speed, eps)


def conflict_risk_matrix(
    vehicles: List[Vehicle], safe_gap: float
) -> Tuple[np.ndarray, np.ndarray]:
    ttcp = np.asarray([compute_ttcp(v) for v in vehicles], dtype=float)
    n = len(vehicles)
    risk = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            delta = abs(ttcp[i] - ttcp[j])
            value = max(0.0, 1.0 - delta / max(safe_gap, 1e-6))
            risk[i, j] = risk[j, i] = value
    return ttcp, risk


def priority_scores(
    vehicles: List[Vehicle], ttcp: np.ndarray, params: TTCPParams
) -> np.ndarray:
    urgency = 1.0 / np.maximum(ttcp, 1e-3)
    urgency /= max(float(np.max(urgency)), 1e-6)
    speed_term = np.asarray([v.speed for v in vehicles]) / max(params.v_max, 1e-6)
    road_term = np.clip(np.asarray([v.road_priority for v in vehicles]), 0.0, 1.0)
    return params.w_t * urgency + params.w_v * speed_term + params.w_r * road_term


def assign_safe_arrival_times(
    vehicles: List[Vehicle],
    ttcp: np.ndarray,
    scores: np.ndarray,
    params: TTCPParams,
) -> Tuple[List[int], np.ndarray]:
    order = list(np.argsort(-scores))
    target = np.zeros(len(vehicles), dtype=float)
    for rank, idx in enumerate(order):
        if rank == 0:
            target[idx] = ttcp[idx]
        else:
            prev = order[rank - 1]
            target[idx] = max(ttcp[idx], target[prev] + params.safe_gap)
    return order, target


def target_controls(
    vehicles: List[Vehicle],
    target_time: np.ndarray,
    params: TTCPParams,
) -> Tuple[np.ndarray, np.ndarray]:
    target_v = np.zeros(len(vehicles))
    target_a = np.zeros(len(vehicles))
    for i, veh in enumerate(vehicles):
        T = max(target_time[i], params.dt)
        target_v[i] = np.clip(
            veh.distance_to_conflict / T, params.v_min, params.v_max
        )
        target_a[i] = np.clip(
            (target_v[i] - veh.speed) / T, params.a_min, params.a_max
        )
    return target_v, target_a


def run_model(vehicles: List[Vehicle], params: TTCPParams) -> Dict[str, object]:
    if not vehicles:
        raise ValueError("vehicles cannot be empty")
    ttcp, risk = conflict_risk_matrix(vehicles, params.safe_gap)
    scores = priority_scores(vehicles, ttcp, params)
    order, target_time = assign_safe_arrival_times(vehicles, ttcp, scores, params)
    target_v, target_a = target_controls(vehicles, target_time, params)
    return {
        "ttcp": ttcp, "risk": risk, "scores": scores, "order": order,
        "target_time": target_time, "target_v": target_v, "target_a": target_a,
    }


def short_trajectory(vehicle, target_v, target_a, horizon, dt):
    t = np.arange(0.0, horizon + 1e-9, dt)
    speed = np.maximum(0.0, vehicle.speed + target_a * t)
    if target_a < 0:
        speed = np.maximum(speed, target_v)
    elif target_a > 0:
        speed = np.minimum(speed, target_v)
    travelled = np.zeros_like(t)
    for k in range(1, len(t)):
        travelled[k] = travelled[k-1] + 0.5 * (speed[k-1] + speed[k]) * dt
    remaining = np.maximum(0.0, vehicle.distance_to_conflict - travelled)
    return t, speed, remaining


def save_outputs(vehicles, result, params, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    ttcp = result["ttcp"]; risk = result["risk"]; scores = result["scores"]
    order = result["order"]; target_time = result["target_time"]
    target_v = result["target_v"]; target_a = result["target_a"]
    ranks = {idx: k + 1 for k, idx in enumerate(order)}

    with (outdir / "ttcp_decision.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([
            "vehicle_id","ttcp_s","risk_max","priority_score","pass_order",
            "target_time_s","target_speed_mps","target_acc_mps2"
        ])
        for i, veh in enumerate(vehicles):
            w.writerow([
                veh.vid, ttcp[i], np.max(risk[i]), scores[i], ranks[i],
                target_time[i], target_v[i], target_a[i]
            ])

    fig = plt.figure(figsize=(6,5))
    plt.imshow(risk, vmin=0, vmax=1)
    plt.colorbar(label="Conflict risk")
    ticks = np.arange(len(vehicles))
    labels = [v.vid for v in vehicles]
    plt.xticks(ticks, labels); plt.yticks(ticks, labels)
    plt.tight_layout()
    fig.savefig(outdir / "conflict_risk_matrix.png", dpi=160); plt.close(fig)

    x = np.arange(len(vehicles))
    fig = plt.figure(figsize=(7,4.5))
    plt.bar(x - 0.18, ttcp, width=0.36, label="Initial TTCP")
    plt.bar(x + 0.18, target_time, width=0.36, label="Coordinated arrival")
    plt.xticks(x, labels); plt.ylabel("Time / s")
    plt.grid(axis="y", alpha=0.25); plt.legend(); plt.tight_layout()
    fig.savefig(outdir / "arrival_time_comparison.png", dpi=160); plt.close(fig)

    fig = plt.figure(figsize=(7,4.5))
    for i, veh in enumerate(vehicles):
        t, speed, remaining = short_trajectory(
            veh, target_v[i], target_a[i], target_time[i], params.dt
        )
        plt.plot(t, remaining, label=veh.vid)
    plt.xlabel("Time / s"); plt.ylabel("Remaining distance / m")
    plt.grid(alpha=0.25); plt.legend(); plt.tight_layout()
    fig.savefig(outdir / "short_trajectories.png", dpi=160); plt.close(fig)


def demo_vehicles():
    return [
        Vehicle("A", 40.0, 10.0, 1.00),
        Vehicle("B", 36.0, 9.2, 0.70),
        Vehicle("C", 52.0, 11.0, 0.65),
        Vehicle("D", 48.0, 10.5, 0.60),
    ]


def main():
    params = TTCPParams()
    vehicles = demo_vehicles()
    result = run_model(vehicles, params)
    print("Pass order:", " -> ".join(vehicles[i].vid for i in result["order"]))
    for i, veh in enumerate(vehicles):
        print(
            f"{veh.vid}: TTCP={result['ttcp'][i]:.2f}s, "
            f"score={result['scores'][i]:.3f}, T*={result['target_time'][i]:.2f}s, "
            f"v*={result['target_v'][i]:.2f}m/s, a*={result['target_a'][i]:.2f}m/s²"
        )
    save_outputs(
        vehicles, result, params,
        Path(__file__).resolve().parent / "outputs"
    )


if __name__ == "__main__":
    main()
