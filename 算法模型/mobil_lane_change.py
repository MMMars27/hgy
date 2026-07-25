from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass
class IDMParams:
    desired_speed: float = 25.0
    max_acc: float = 1.5
    comfortable_brake: float = 2.0
    desired_headway: float = 1.5
    min_gap: float = 2.0
    delta: float = 4.0


def idm_acceleration(
    ego_speed: float,
    front_speed: float,
    gap: float,
    params: IDMParams,
) -> float:
    if gap <= 0.0:
        return -10.0

    dv = ego_speed - front_speed
    denom = 2.0 * math.sqrt(
        max(params.max_acc * params.comfortable_brake, 1e-9)
    )
    s_star = params.min_gap + max(
        0.0,
        ego_speed * params.desired_headway + ego_speed * dv / denom
    )
    free_term = (ego_speed / max(params.desired_speed, 1e-6)) ** params.delta
    interaction_term = (s_star / max(gap, 1e-6)) ** 2
    return params.max_acc * (1.0 - free_term - interaction_term)


from dataclasses import dataclass


@dataclass
class MOBILParams:
    politeness: float = 0.3
    incentive_threshold: float = 0.2
    safe_brake: float = 3.0


@dataclass
class MOBILResult:
    lane_change: bool
    incentive: float
    ego_old_acc: float
    ego_new_acc: float
    rear_old_acc: float
    rear_new_acc: float
    safety_ok: bool
    incentive_ok: bool


def mobil_decision(
    ego_old_acc: float,
    ego_new_acc: float,
    rear_old_acc: float,
    rear_new_acc: float,
    params: MOBILParams,
) -> MOBILResult:
    incentive = (
        (ego_new_acc - ego_old_acc)
        + params.politeness * (rear_new_acc - rear_old_acc)
    )
    safety_ok = rear_new_acc >= -params.safe_brake
    incentive_ok = incentive > params.incentive_threshold
    return MOBILResult(
        lane_change=bool(safety_ok and incentive_ok),
        incentive=float(incentive),
        ego_old_acc=float(ego_old_acc),
        ego_new_acc=float(ego_new_acc),
        rear_old_acc=float(rear_old_acc),
        rear_new_acc=float(rear_new_acc),
        safety_ok=bool(safety_ok),
        incentive_ok=bool(incentive_ok),
    )


from pathlib import Path
import csv
import matplotlib.pyplot as plt
import numpy as np


def quintic_lane_change(x0, speed, lane_width, duration=4.0, dt=0.05):
    t = np.arange(0.0, duration + 1e-9, dt)
    tau = t / duration
    y = lane_width * (10*tau**3 - 15*tau**4 + 6*tau**5)
    x = x0 + speed * t
    return t, x, y


def run_demo():
    idm = IDMParams()
    mobil = MOBILParams(politeness=0.3, incentive_threshold=0.2, safe_brake=3.0)

    ego_v = 18.0
    current_front_v = 15.0
    current_front_gap = 20.0
    target_front_v = 22.0
    target_front_gap = 35.0
    target_rear_v = 17.0
    target_rear_gap_to_ego = 25.0
    vehicle_length = 4.5

    rear_old_gap = target_rear_gap_to_ego + vehicle_length + target_front_gap

    ego_old_acc = idm_acceleration(ego_v, current_front_v, current_front_gap, idm)
    ego_new_acc = idm_acceleration(ego_v, target_front_v, target_front_gap, idm)
    rear_old_acc = idm_acceleration(target_rear_v, target_front_v, rear_old_gap, idm)
    rear_new_acc = idm_acceleration(target_rear_v, ego_v, target_rear_gap_to_ego, idm)

    result = mobil_decision(
        ego_old_acc, ego_new_acc, rear_old_acc, rear_new_acc, mobil
    )
    scenario = {
        "ego_v": ego_v,
        "current_front_gap": current_front_gap,
        "target_front_gap": target_front_gap,
        "target_rear_gap_to_ego": target_rear_gap_to_ego,
    }
    return result, scenario


def save_outputs(result, scenario, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    with (outdir / "mobil_result.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["item", "value"])
        for key, value in [
            ("ego_old_acc_mps2", result.ego_old_acc),
            ("ego_new_acc_mps2", result.ego_new_acc),
            ("rear_old_acc_mps2", result.rear_old_acc),
            ("rear_new_acc_mps2", result.rear_new_acc),
            ("incentive_mps2", result.incentive),
            ("safety_ok", result.safety_ok),
            ("incentive_ok", result.incentive_ok),
            ("lane_change", result.lane_change),
        ]:
            w.writerow([key, value])

    labels = ["Ego old", "Ego new", "Rear old", "Rear new"]
    vals = [
        result.ego_old_acc, result.ego_new_acc,
        result.rear_old_acc, result.rear_new_acc
    ]
    fig = plt.figure(figsize=(7, 4.5))
    plt.bar(np.arange(len(vals)), vals)
    plt.axhline(0.0, linewidth=1)
    plt.xticks(np.arange(len(vals)), labels)
    plt.ylabel("Predicted acceleration / m/s²")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    fig.savefig(outdir / "acceleration_comparison.png", dpi=160)
    plt.close(fig)

    fig = plt.figure(figsize=(9, 4.5))
    plt.axhline(0.0, linewidth=1)
    plt.axhline(3.5, linewidth=1)
    plt.axhline(7.0, linewidth=1)

    if result.lane_change:
        _, x, y = quintic_lane_change(0.0, scenario["ego_v"], 3.5)
    else:
        x = np.linspace(0, 70, 100)
        y = np.zeros_like(x)

    plt.plot(x, y, linewidth=2, label="Ego")
    plt.scatter([scenario["current_front_gap"]], [0.0], marker="s", s=80, label="Current front")
    plt.scatter([scenario["target_front_gap"]], [3.5], marker="s", s=80, label="Target front")
    plt.scatter([-scenario["target_rear_gap_to_ego"]], [3.5], marker="s", s=80, label="Target rear")
    plt.xlabel("Longitudinal position / m")
    plt.ylabel("Lateral position / m")
    plt.ylim(-1.0, 8.0)
    plt.grid(alpha=0.25)
    plt.legend(ncol=2)
    plt.tight_layout()
    fig.savefig(outdir / "lane_change_schematic.png", dpi=160)
    plt.close(fig)


def main():
    result, scenario = run_demo()
    print(f"Ego old acc: {result.ego_old_acc:.3f} m/s²")
    print(f"Ego new acc: {result.ego_new_acc:.3f} m/s²")
    print(f"Rear old acc: {result.rear_old_acc:.3f} m/s²")
    print(f"Rear new acc: {result.rear_new_acc:.3f} m/s²")
    print(f"MOBIL incentive: {result.incentive:.3f} m/s²")
    print(f"Safety condition: {result.safety_ok}")
    print(f"Incentive condition: {result.incentive_ok}")
    print("Decision:", "CHANGE LANE" if result.lane_change else "KEEP LANE")
    save_outputs(result, scenario, Path(__file__).resolve().parent / "outputs")


if __name__ == "__main__":
    main()
