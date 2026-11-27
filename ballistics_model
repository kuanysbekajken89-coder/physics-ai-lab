import numpy as np
import pandas as pd


def simulate_flight(
    v0: float,
    angle_deg: float,
    mass_kg: float,
    area_m2: float = 0.02,
    cd: float = 0.47,
    rho: float = 1.225,
    g: float = 9.81,
    dt: float = 0.02,
    max_steps: int = 10000,
) -> pd.DataFrame:
    theta = np.radians(angle_deg)
    vx = v0 * np.cos(theta)
    vy = v0 * np.sin(theta)
    x = 0.0
    y = 0.0
    t = 0.0

    k_drag = (0.5 * rho * cd * area_m2) / mass_kg
    rows = [{"t_s": 0.0, "x_m": 0.0, "y_m": 0.0, "v_ms": float(v0)}]

    for _ in range(max_steps):
        speed = np.hypot(vx, vy)
        ax = -k_drag * vx * speed
        ay = -g - k_drag * vy * speed

        vx_next = vx + ax * dt
        vy_next = vy + ay * dt
        x_next = x + vx * dt + 0.5 * ax * (dt ** 2)
        y_next = y + vy * dt + 0.5 * ay * (dt ** 2)
        t_next = t + dt

        if y_next < 0:
            frac = -y / (y_next - y) if abs(y_next - y) > 1e-9 else 0.0
            x_land = x + frac * (x_next - x)
            t_land = t + frac * dt
            v_land = np.hypot(vx + frac * (vx_next - vx), vy + frac * (vy_next - vy))
            rows.append({
                "t_s": round(float(t_land), 3),
                "x_m": round(float(x_land), 2),
                "y_m": 0.0,
                "v_ms": round(float(v_land), 2),
            })
            break

        x, y = x_next, y_next
        vx, vy = vx_next, vy_next
        t = t_next

        rows.append({
            "t_s": round(float(t), 3),
            "x_m": round(float(x), 2),
            "y_m": round(float(y), 2),
            "v_ms": round(float(np.hypot(vx, vy)), 2),
        })

    return pd.DataFrame(rows)


def get_flight_summary(df: pd.DataFrame, v0: float, angle_deg: float, mass_kg: float, cd: float) -> dict:
    return {
        "v0_ms": v0,
        "angle_deg": angle_deg,
        "mass_kg": mass_kg,
        "cd": cd,
        "range_m": round(float(df["x_m"].max()), 2),
        "max_height_m": round(float(df["y_m"].max()), 2),
        "flight_time_s": round(float(df["t_s"].max()), 2),
        "impact_speed_ms": round(float(df.iloc[-1]["v_ms"]), 2),
    }
