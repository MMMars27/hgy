from __future__ import annotations

import numpy as np


class QuinticPolynomial:
    def __init__(self, xs, vxs, axs, xe, vxe, axe, T):
        if T <= 0:
            raise ValueError("T must be positive")
        self.a0 = xs
        self.a1 = vxs
        self.a2 = axs / 2.0
        A = np.array([
            [T**3, T**4, T**5],
            [3*T**2, 4*T**3, 5*T**4],
            [6*T, 12*T**2, 20*T**3],
        ], dtype=float)
        b = np.array([
            xe - self.a0 - self.a1*T - self.a2*T**2,
            vxe - self.a1 - 2*self.a2*T,
            axe - 2*self.a2,
        ], dtype=float)
        self.a3, self.a4, self.a5 = np.linalg.solve(A, b)

    def calc(self, t):
        return self.a0 + self.a1*t + self.a2*t**2 + self.a3*t**3 + self.a4*t**4 + self.a5*t**5

    def d1(self, t):
        return self.a1 + 2*self.a2*t + 3*self.a3*t**2 + 4*self.a4*t**3 + 5*self.a5*t**4

    def d2(self, t):
        return 2*self.a2 + 6*self.a3*t + 12*self.a4*t**2 + 20*self.a5*t**3

    def d3(self, t):
        return 6*self.a3 + 24*self.a4*t + 60*self.a5*t**2


class QuarticPolynomial:
    def __init__(self, xs, vxs, axs, vxe, axe, T):
        if T <= 0:
            raise ValueError("T must be positive")
        self.b0 = xs
        self.b1 = vxs
        self.b2 = axs / 2.0
        A = np.array([
            [3*T**2, 4*T**3],
            [6*T, 12*T**2],
        ], dtype=float)
        b = np.array([
            vxe - self.b1 - 2*self.b2*T,
            axe - 2*self.b2,
        ], dtype=float)
        self.b3, self.b4 = np.linalg.solve(A, b)

    def calc(self, t):
        return self.b0 + self.b1*t + self.b2*t**2 + self.b3*t**3 + self.b4*t**4

    def d1(self, t):
        return self.b1 + 2*self.b2*t + 3*self.b3*t**2 + 4*self.b4*t**3

    def d2(self, t):
        return 2*self.b2 + 6*self.b3*t + 12*self.b4*t**2

    def d3(self, t):
        return 6*self.b3 + 24*self.b4*t


import numpy as np


def check_dynamic_constraints(traj, v_max, a_max, a_lat_max):
    if np.any(traj.v < -1e-6):
        return False
    if np.any(traj.v > v_max + 1e-6):
        return False
    if np.any(np.abs(traj.a) > a_max + 1e-6):
        return False
    if np.any(np.abs(traj.d_ddot) > a_lat_max + 1e-6):
        return False
    return True


def collision_with_neighbors(traj, neighbors, safe_dist):
    min_dist = float("inf")
    for n in neighbors:
        n_s = n.s0 + n.v * traj.t
        n_d = np.full_like(traj.t, n.d0)
        dist = np.sqrt((traj.s - n_s)**2 + (traj.d - n_d)**2)
        min_dist = min(min_dist, float(np.min(dist)))
        if np.any(dist < safe_dist):
            return True, min_dist
    return False, min_dist


from dataclasses import dataclass
from typing import List
import numpy as np


@dataclass
class EgoState:
    s: float
    d: float
    v: float
    a: float
    d_dot: float = 0.0
    d_ddot: float = 0.0


@dataclass
class Neighbor:
    vid: str
    s0: float
    d0: float
    v: float


@dataclass
class PlannerParams:
    dt: float = 0.1
    target_d: float = 3.5
    t_set: tuple = (3.0, 4.0, 5.0)
    v_set: tuple = (9.0, 10.5, 12.0)
    v_ref: float = 11.0
    v_max: float = 15.0
    a_max: float = 3.0
    a_lat_max: float = 2.0
    safe_dist: float = 5.0
    w_jerk: float = 0.12
    w_speed: float = 1.0
    w_time: float = 0.08


@dataclass
class Trajectory:
    T: float
    v_target: float
    t: np.ndarray
    s: np.ndarray
    d: np.ndarray
    v: np.ndarray
    a: np.ndarray
    s_jerk: np.ndarray
    d_dot: np.ndarray
    d_ddot: np.ndarray
    d_jerk: np.ndarray
    cost: float = float("inf")
    min_neighbor_dist: float = float("inf")
    feasible: bool = False
    reason: str = ""


def sample_trajectory(ego, T, v_target, params):
    lat = QuinticPolynomial(
        ego.d, ego.d_dot, ego.d_ddot,
        params.target_d, 0.0, 0.0, T
    )
    lon = QuarticPolynomial(
        ego.s, ego.v, ego.a,
        v_target, 0.0, T
    )
    t = np.arange(0.0, T + 1e-9, params.dt)
    return Trajectory(
        T=T, v_target=v_target, t=t,
        s=np.asarray([lon.calc(x) for x in t]),
        d=np.asarray([lat.calc(x) for x in t]),
        v=np.asarray([lon.d1(x) for x in t]),
        a=np.asarray([lon.d2(x) for x in t]),
        s_jerk=np.asarray([lon.d3(x) for x in t]),
        d_dot=np.asarray([lat.d1(x) for x in t]),
        d_ddot=np.asarray([lat.d2(x) for x in t]),
        d_jerk=np.asarray([lat.d3(x) for x in t]),
    )


def trajectory_cost(traj, params):
    jerk_integral = float(np.trapezoid(traj.s_jerk**2 + traj.d_jerk**2, traj.t))
    speed_error = float((traj.v[-1] - params.v_ref)**2)
    return params.w_jerk * jerk_integral + params.w_speed * speed_error + params.w_time * traj.T


def generate_candidates(ego, neighbors, params):
    candidates: List[Trajectory] = []
    for T in params.t_set:
        for v_target in params.v_set:
            traj = sample_trajectory(ego, float(T), float(v_target), params)
            if not check_dynamic_constraints(traj, params.v_max, params.a_max, params.a_lat_max):
                traj.reason = "dynamic_constraint"
                candidates.append(traj)
                continue

            collision, min_dist = collision_with_neighbors(traj, neighbors, params.safe_dist)
            traj.min_neighbor_dist = min_dist
            if collision:
                traj.reason = "collision"
                candidates.append(traj)
                continue

            traj.cost = trajectory_cost(traj, params)
            traj.feasible = True
            traj.reason = "feasible"
            candidates.append(traj)
    return candidates


def choose_best(candidates):
    feasible = [x for x in candidates if x.feasible]
    if not feasible:
        raise RuntimeError("No feasible trajectory. Relax constraints or modify the scenario.")
    return min(feasible, key=lambda x: x.cost)


from pathlib import Path
import csv
import matplotlib.pyplot as plt
import numpy as np


def save_outputs(candidates, best, neighbors, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)

    with (outdir / "candidate_summary.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([
            "T_s","v_target_mps","feasible","reason","cost",
            "min_neighbor_distance_m","max_abs_long_acc_mps2","max_abs_lat_acc_mps2"
        ])
        for tr in candidates:
            w.writerow([
                tr.T, tr.v_target, tr.feasible, tr.reason,
                "" if not np.isfinite(tr.cost) else tr.cost,
                "" if not np.isfinite(tr.min_neighbor_dist) else tr.min_neighbor_dist,
                np.max(np.abs(tr.a)), np.max(np.abs(tr.d_ddot))
            ])

    with (outdir / "best_trajectory.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["t_s","s_m","d_m","v_mps","a_mps2","lat_acc_mps2"])
        for row in zip(best.t, best.s, best.d, best.v, best.a, best.d_ddot):
            w.writerow(row)

    fig = plt.figure(figsize=(9,5))
    for tr in candidates:
        if tr.feasible:
            plt.plot(tr.s, tr.d, alpha=0.5)
    plt.plot(best.s, best.d, linewidth=2.5, label="Best trajectory")
    for n in neighbors:
        plt.scatter(n.s0, n.d0, marker="s", s=70)
        plt.text(n.s0, n.d0+0.15, n.vid)
    plt.axhline(0.0, linewidth=1); plt.axhline(3.5, linewidth=1)
    plt.xlabel("Longitudinal s / m"); plt.ylabel("Lateral d / m")
    plt.grid(alpha=0.25); plt.legend(); plt.tight_layout()
    fig.savefig(outdir / "candidate_and_best_trajectories.png", dpi=160); plt.close(fig)

    labels = [f"T{tr.T:g}-V{tr.v_target:g}" for tr in candidates]
    values = [tr.cost if tr.feasible else 0.0 for tr in candidates]
    fig = plt.figure(figsize=(9,4.8))
    x = np.arange(len(labels))
    plt.bar(x, values)
    plt.xticks(x, labels, rotation=35, ha="right")
    plt.ylabel("Trajectory cost (0 means infeasible here)")
    plt.grid(axis="y", alpha=0.25); plt.tight_layout()
    fig.savefig(outdir / "candidate_costs.png", dpi=160); plt.close(fig)

    fig = plt.figure(figsize=(8,4.8))
    plt.plot(best.t, best.v, label="Speed")
    plt.plot(best.t, best.a, label="Longitudinal acceleration")
    plt.plot(best.t, best.d_ddot, label="Lateral acceleration")
    plt.xlabel("Time / s"); plt.grid(alpha=0.25); plt.legend(); plt.tight_layout()
    fig.savefig(outdir / "best_speed_acceleration.png", dpi=160); plt.close(fig)


def main():
    ego = EgoState(s=0.0, d=0.0, v=10.0, a=0.0)
    neighbors = [
        Neighbor("current_front", s0=30.0, d0=0.0, v=6.0),
        Neighbor("target_front", s0=47.0, d0=3.5, v=11.5),
        Neighbor("target_rear", s0=-18.0, d0=3.5, v=10.5),
    ]
    params = PlannerParams()
    candidates = generate_candidates(ego, neighbors, params)
    best = choose_best(candidates)
    feasible_num = sum(x.feasible for x in candidates)

    print(f"Candidates: {len(candidates)}, feasible: {feasible_num}")
    print(
        f"Best: T={best.T:.1f}s, v_target={best.v_target:.1f}m/s, "
        f"cost={best.cost:.3f}, min_dist={best.min_neighbor_dist:.3f}m"
    )
    print(
        f"Max |long acc|={np.max(np.abs(best.a)):.3f}m/s², "
        f"Max |lat acc|={np.max(np.abs(best.d_ddot)):.3f}m/s²"
    )
    save_outputs(candidates, best, neighbors, Path(__file__).resolve().parent / "outputs")


if __name__ == "__main__":
    main()
