from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import numpy as np


@dataclass
class MovingObject:
    oid: str
    position: np.ndarray
    velocity: np.ndarray
    radius: float


def closest_approach(
    ego_position: np.ndarray,
    candidate_velocity: np.ndarray,
    other: MovingObject,
    horizon: float,
) -> Tuple[float, float]:
    r = np.asarray(ego_position, dtype=float) - np.asarray(other.position, dtype=float)
    u = np.asarray(candidate_velocity, dtype=float) - np.asarray(other.velocity, dtype=float)
    denom = float(np.dot(u, u))
    if denom < 1e-12:
        t_ca = 0.0
    else:
        t_ca = float(np.clip(-np.dot(r, u) / denom, 0.0, horizon))
    d_min = float(np.linalg.norm(r + u * t_ca))
    return t_ca, d_min


def is_velocity_obstacle(
    ego_position: np.ndarray,
    ego_radius: float,
    candidate_velocity: np.ndarray,
    other: MovingObject,
    horizon: float,
    safety_margin: float,
) -> Tuple[bool, float, float]:
    combined_radius = ego_radius + other.radius + safety_margin
    current_distance = float(np.linalg.norm(np.asarray(ego_position) - np.asarray(other.position)))
    if current_distance <= combined_radius:
        return True, 0.0, current_distance

    t_ca, d_min = closest_approach(
        ego_position, candidate_velocity, other, horizon
    )
    unsafe = bool(t_ca > 1e-9 and t_ca <= horizon and d_min < combined_radius)
    return unsafe, t_ca, d_min


import numpy as np


def sample_velocities(
    v_max: float,
    speed_step: float,
    heading_min_deg: float,
    heading_max_deg: float,
    heading_step_deg: float,
) -> np.ndarray:
    if speed_step <= 0 or heading_step_deg <= 0:
        raise ValueError("Sampling steps must be positive")

    speeds = np.arange(0.0, v_max + 1e-9, speed_step)
    headings = np.deg2rad(
        np.arange(heading_min_deg, heading_max_deg + 1e-9, heading_step_deg)
    )

    velocities = []
    for speed in speeds:
        if speed < 1e-9:
            velocities.append([0.0, 0.0])
        else:
            for theta in headings:
                velocities.append([
                    speed * np.cos(theta),
                    speed * np.sin(theta),
                ])
    return np.asarray(velocities, dtype=float)


import math
import numpy as np


def velocity_cost(
    candidate: np.ndarray,
    desired: np.ndarray,
    current: np.ndarray,
    min_distances,
    combined_radii,
    w_des: float = 1.0,
    w_change: float = 0.20,
    w_risk: float = 0.50,
) -> float:
    candidate = np.asarray(candidate, dtype=float)
    desired = np.asarray(desired, dtype=float)
    current = np.asarray(current, dtype=float)

    des_term = float(np.sum((candidate - desired) ** 2))
    change_term = float(np.sum((candidate - current) ** 2))
    risk_term = 0.0
    for d, R in zip(min_distances, combined_radii):
        risk_term += math.exp(-float(d) / max(float(R), 1e-6))

    return w_des * des_term + w_change * change_term + w_risk * risk_term


from pathlib import Path
import csv, math
import matplotlib.pyplot as plt
import numpy as np


def run_velocity_obstacle_planner(
    ego_position,
    ego_velocity,
    desired_velocity,
    ego_radius,
    others,
    horizon=4.0,
    safety_margin=0.4,
    v_max=10.5,
    speed_step=0.5,
    heading_min_deg=-45.0,
    heading_max_deg=45.0,
    heading_step_deg=3.0,
):
    candidates = sample_velocities(
        v_max, speed_step, heading_min_deg, heading_max_deg, heading_step_deg
    )
    records = []
    safe = []

    for vel in candidates:
        unsafe_any = False
        min_dists = []
        combined_radii = []

        for obj in others:
            unsafe, t_ca, d_min = is_velocity_obstacle(
                ego_position, ego_radius, vel, obj, horizon, safety_margin
            )
            min_dists.append(d_min)
            combined_radii.append(ego_radius + obj.radius + safety_margin)
            if unsafe:
                unsafe_any = True

        if unsafe_any:
            records.append((vel, False, math.inf, min_dists))
            continue

        cost = velocity_cost(
            vel, desired_velocity, ego_velocity, min_dists, combined_radii
        )
        records.append((vel, True, cost, min_dists))
        safe.append((vel, cost, min_dists))

    if not safe:
        raise RuntimeError("No safe candidate velocity found.")

    best_vel, best_cost, best_dists = min(safe, key=lambda x: x[1])
    return candidates, records, best_vel, best_cost, best_dists


def save_outputs(
    records, best_vel, best_cost, best_dists,
    ego_position, desired_velocity, others, horizon, outdir: Path
):
    outdir.mkdir(parents=True, exist_ok=True)

    with (outdir / "velocity_candidates.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(
            ["vx","vy","safe","cost"]
            + [f"min_dist_to_{obj.oid}" for obj in others]
        )
        for vel, is_safe, cost, min_dists in records:
            w.writerow([
                vel[0], vel[1], is_safe,
                "" if not np.isfinite(cost) else cost,
                *min_dists
            ])

    speed = float(np.linalg.norm(best_vel))
    heading = math.degrees(math.atan2(best_vel[1], best_vel[0]))
    (outdir / "best_velocity.txt").write_text(
        f"best_vx={best_vel[0]:.6f}\n"
        f"best_vy={best_vel[1]:.6f}\n"
        f"best_speed={speed:.6f}\n"
        f"best_heading_deg={heading:.6f}\n"
        f"best_cost={best_cost:.6f}\n"
        f"min_distances={best_dists}\n",
        encoding="utf-8"
    )

    safe_xy = np.array([r[0] for r in records if r[1]])
    unsafe_xy = np.array([r[0] for r in records if not r[1]])

    fig = plt.figure(figsize=(7,7))
    if len(unsafe_xy):
        plt.scatter(unsafe_xy[:,0], unsafe_xy[:,1], s=8, alpha=0.35, label="Unsafe velocity")
    if len(safe_xy):
        plt.scatter(safe_xy[:,0], safe_xy[:,1], s=8, alpha=0.45, label="Safe velocity")
    plt.scatter([desired_velocity[0]], [desired_velocity[1]], marker="*", s=140, label="Desired")
    plt.scatter([best_vel[0]], [best_vel[1]], marker="X", s=110, label="Best")
    plt.xlabel("v_x / m/s"); plt.ylabel("v_y / m/s")
    plt.axis("equal"); plt.grid(alpha=0.25); plt.legend(); plt.tight_layout()
    fig.savefig(outdir / "velocity_space.png", dpi=160); plt.close(fig)

    fig = plt.figure(figsize=(8,6))
    ts = np.linspace(0.0, horizon, 80)
    ego_pred = ego_position[None,:] + ts[:,None] * best_vel[None,:]
    plt.plot(ego_pred[:,0], ego_pred[:,1], linewidth=2.3, label="Ego")
    plt.scatter([ego_position[0]], [ego_position[1]], marker="o", s=70)

    for obj in others:
        pred = obj.position[None,:] + ts[:,None] * obj.velocity[None,:]
        plt.plot(pred[:,0], pred[:,1], label=obj.oid)
        plt.scatter([obj.position[0]], [obj.position[1]], marker="s", s=55)

    plt.xlabel("x / m"); plt.ylabel("y / m")
    plt.axis("equal"); plt.grid(alpha=0.25); plt.legend(); plt.tight_layout()
    fig.savefig(outdir / "predicted_motion.png", dpi=160); plt.close(fig)


def main():
    ego_position = np.array([0.0, 0.0])
    ego_velocity = np.array([7.5, 0.0])
    desired_velocity = np.array([9.0, 0.0])
    ego_radius = 1.4

    others = [
        MovingObject("obj1", np.array([10.0, 0.0]), np.array([5.5, 0.0]), 1.4),
        MovingObject("obj2", np.array([16.0, -3.0]), np.array([6.0, 0.5]), 1.4),
        MovingObject("obj3", np.array([12.0, 13.0]), np.array([2.0, -1.0]), 1.4),
    ]
    horizon = 4.0

    candidates, records, best_vel, best_cost, best_dists = (
        run_velocity_obstacle_planner(
            ego_position, ego_velocity, desired_velocity, ego_radius, others,
            horizon=horizon, safety_margin=0.4, v_max=10.5,
            speed_step=0.5, heading_min_deg=-45.0,
            heading_max_deg=45.0, heading_step_deg=3.0,
        )
    )

    speed = float(np.linalg.norm(best_vel))
    heading = math.degrees(math.atan2(best_vel[1], best_vel[0]))
    safe_count = sum(1 for x in records if x[1])

    print(f"Candidates: {len(candidates)}, safe: {safe_count}")
    print(
        f"Best velocity=({best_vel[0]:.3f},{best_vel[1]:.3f})m/s, "
        f"speed={speed:.3f}m/s, heading={heading:.2f}deg"
    )
    print(f"Best cost={best_cost:.4f}")
    print("Minimum predicted distances:", [round(x,3) for x in best_dists])

    save_outputs(
        records, best_vel, best_cost, best_dists,
        ego_position, desired_velocity, others, horizon,
        Path(__file__).resolve().parent / "outputs"
    )


if __name__ == "__main__":
    main()
