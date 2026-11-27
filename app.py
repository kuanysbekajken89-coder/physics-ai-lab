import os
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from google import genai

from ballistics_model import get_flight_summary, simulate_flight

st.set_page_config(
    page_title="AeroLab — Grade 11 Projectile & Drag Lab",
    page_icon="🧪",
    layout="wide",
)

# --- Modern Lab Styling ---
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
        }
        .hero-box {
            background: linear-gradient(120deg, #0b132b 0%, #1c2541 55%, #2563eb 100%);
            padding: 24px 28px;
            border-radius: 18px;
            color: #ffffff;
            margin-bottom: 20px;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.12);
        }
        .hero-badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.16);
            border: 1px solid rgba(255, 255, 255, 0.25);
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            margin-bottom: 10px;
        }
        .hero-title {
            margin: 0 0 6px 0;
            font-size: 1.75rem;
            font-weight: 700;
            color: #ffffff;
        }
        .hero-subtitle {
            margin: 0;
            font-size: 0.98rem;
            color: #dbeafe;
        }
        .kpi-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-top: 4px solid #2563eb;
            border-radius: 14px;
            padding: 16px 18px;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
        }
        .kpi-card.teal {
            border-top-color: #0d9488;
        }
        .kpi-card.amber {
            border-top-color: #d97706;
        }
        .kpi-card.indigo {
            border-top-color: #4f46e5;
        }
        .kpi-title {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #64748b;
            font-weight: 600;
            margin-bottom: 6px;
        }
        .kpi-main {
            font-size: 1.5rem;
            font-weight: 700;
            color: #0f172a;
            line-height: 1.15;
        }
        .kpi-sub {
            font-size: 0.82rem;
            color: #475569;
            margin-top: 6px;
        }
        .ai-panel {
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 16px;
            padding: 20px 22px;
            margin-top: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Session State Defaults ---
defaults = {
    "v0": 35.0,
    "angle_deg": 40.0,
    "mass_kg": 2.5,
    "cd": 0.30,
    "area_m2": 0.02,
    "question": "Why does air drag reduce range and how does increasing mass change the trajectory?",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def set_preset(v0, angle_deg, mass_kg, cd, area_m2):
    st.session_state["v0"] = v0
    st.session_state["angle_deg"] = angle_deg
    st.session_state["mass_kg"] = mass_kg
    st.session_state["cd"] = cd
    st.session_state["area_m2"] = area_m2


def set_quick_question(q_text):
    st.session_state["question"] = q_text


# --- Hero Header ---
st.markdown(
    """
    <div class="hero-box">
        <div class="hero-badge">GRADE 11 PHYSICS & ENGINEERING SANDBOX</div>
        <h1 class="hero-title">AeroLab: Projectile Motion & Air Resistance</h1>
        <p class="hero-subtitle">Explore how launch angle, mass, and aerodynamic drag reshape flight trajectories compared to an ideal vacuum model.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Presets Row ---
st.markdown("#### Quick Scenarios")
b1, b2, b3, b4 = st.columns(4)
with b1:
    st.button(
        "⚽ Soccer Ball",
        use_container_width=True,
        on_click=set_preset,
        args=(28.0, 38.0, 0.45, 0.47, 0.038),
    )
with b2:
    st.button(
        "🚀 Streamlined Probe",
        use_container_width=True,
        on_click=set_preset,
        args=(45.0, 42.0, 3.0, 0.12, 0.015),
    )
with b3:
    st.button(
        "🪨 Heavy Rock",
        use_container_width=True,
        on_click=set_preset,
        args=(35.0, 45.0, 8.0, 0.55, 0.020),
    )
with b4:
    st.button(
        "↺ Reset Defaults",
        use_container_width=True,
        on_click=set_preset,
        args=(35.0, 40.0, 2.5, 0.30, 0.020),
    )

# --- Sidebar Controls ---
st.sidebar.header("Launch Parameters")
v0 = st.sidebar.slider("Initial Speed v₀ (m/s)", 5.0, 80.0, step=1.0, key="v0")
angle_deg = st.sidebar.slider("Launch Angle α (deg)", 5.0, 85.0, step=1.0, key="angle_deg")
mass_kg = st.sidebar.slider("Object Mass m (kg)", 0.2, 20.0, step=0.1, key="mass_kg")
cd = st.sidebar.slider("Drag Coefficient C_d", 0.05, 1.20, step=0.01, key="cd")
area_m2 = st.sidebar.slider("Cross-Section Area A (m²)", 0.005, 0.200, step=0.005, key="area_m2")

st.sidebar.divider()
show_ideal = st.sidebar.checkbox("Overlay Ideal Vacuum Trajectory", value=True)
show_table = st.sidebar.checkbox("Show Comparison Table", value=True)

# --- Simulations ---
df = simulate_flight(v0, angle_deg, mass_kg, area_m2=area_m2, cd=cd)
summary = get_flight_summary(df, v0, angle_deg, mass_kg, cd)

g = 9.81
rad = np.radians(angle_deg)
t_ideal = float((2.0 * v0 * np.sin(rad)) / g)
range_ideal = round(float((v0 ** 2) * np.sin(2.0 * rad) / g), 2)
height_ideal = round(float(((v0 * np.sin(rad)) ** 2) / (2.0 * g)), 2)
t_ideal_round = round(t_ideal, 2)

t_arr = np.linspace(0.0, t_ideal, 160)
x_ideal = v0 * np.cos(rad) * t_arr
y_ideal = v0 * np.sin(rad) * t_arr - 0.5 * g * (t_arr ** 2)

diff_range = round(summary["range_m"] - range_ideal, 2)
diff_height = round(summary["max_height_m"] - height_ideal, 2)
diff_time = round(summary["flight_time_s"] - t_ideal_round, 2)

# --- KPI Cards ---
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Horizontal Range</div>
            <div class="kpi-main">{summary['range_m']} m</div>
            <div class="kpi-sub">vs Vacuum: <b>{diff_range:+.2f} m</b> ({range_ideal} m)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        f"""
        <div class="kpi-card teal">
            <div class="kpi-title">Peak Altitude</div>
            <div class="kpi-main">{summary['max_height_m']} m</div>
            <div class="kpi-sub">vs Vacuum: <b>{diff_height:+.2f} m</b> ({height_ideal} m)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        f"""
        <div class="kpi-card indigo">
            <div class="kpi-title">Flight Duration</div>
            <div class="kpi-main">{summary['flight_time_s']} s</div>
            <div class="kpi-sub">vs Vacuum: <b>{diff_time:+.2f} s</b> ({t_ideal_round} s)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(
        f"""
        <div class="kpi-card amber">
            <div class="kpi-title">Impact Speed</div>
            <div class="kpi-main">{summary['impact_speed_ms']} m/s</div>
            <div class="kpi-sub">Launch Speed: <b>{v0} m/s</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# --- Chart & Comparison Table ---
chart_col, table_col = st.columns([2.2, 1.0] if show_table else [1.0, 0.001])

with chart_col:
    fig = go.Figure()

    if show_ideal:
        fig.add_trace(
            go.Scatter(
                x=x_ideal,
                y=y_ideal,
                mode="lines",
                name="Ideal Vacuum (No Drag)",
                line=dict(color="#94a3b8", width=2.2, dash="dash"),
            )
        )

    fig.add_trace(
        go.Scatter(
            x=df["x_m"],
            y=df["y_m"],
            mode="lines",
            name="With Air Drag",
            line=dict(color="#2563eb", width=3.5),
            fill="tozeroy",
            fillcolor="rgba(37, 99, 235, 0.08)",
        )
    )

    fig.update_layout(
        template="plotly_white",
        title="Trajectory Comparison (x vs. y)",
        xaxis_title="Horizontal Distance x (m)",
        yaxis_title="Vertical Height y (m)",
        height=430,
        margin=dict(l=20, r=20, t=48, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

if show_table:
    with table_col:
        st.markdown("#### Model Comparison")
        comp_df = pd.DataFrame(
            {
                "Metric": ["Range (m)", "Max Height (m)", "Time (s)", "Delta Range (m)"],
                "With Drag": [summary["range_m"], summary["max_height_m"], summary["flight_time_s"], diff_range],
                "No Drag": [range_ideal, height_ideal, t_ideal_round, 0.0],
            }
        )
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

        st.caption(
            f"Drag factor k = (0.5 · ρ · C_d · A) / m with ρ = 1.225 kg/m³, g = 9.81 m/s²."
        )

# --- AI Physics Tutor ---
st.markdown('<div class="ai-panel">', unsafe_allow_html=True)
st.markdown("### 🤖 AI Physics Lab Assistant")

q1, q2, q3 = st.columns(3)
with q1:
    st.button(
        "Explain range loss",
        use_container_width=True,
        on_click=set_quick_question,
        args=("Explain why the real range with air drag differs from the ideal vacuum range in this run.",),
    )
with q2:
    st.button(
        "How to fly farther?",
        use_container_width=True,
        on_click=set_quick_question,
        args=("Which parameter (angle, mass, or drag coefficient C_d) gives the biggest range boost here and why?",),
    )
with q3:
    st.button(
        "Make a 1-question check",
        use_container_width=True,
        on_click=set_quick_question,
        args=("Create one short Grade 11 physics check question based on the current numbers, with a brief hint.",),
    )

question = st.text_input("Ask a question about this experiment", key="question")

if st.button("Analyze with AI", type="primary"):
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.warning("Please add GEMINI_API_KEY in Streamlit Secrets to enable AI responses.")
    else:
        payload = {
            "current_with_drag": summary,
            "ideal_vacuum": {
                "range_m": range_ideal,
                "max_height_m": height_ideal,
                "flight_time_s": t_ideal_round,
                "range_diff_m": diff_range,
            },
        }
        client = genai.Client(api_key=api_key)
        prompt = (
            "You are a clear, encouraging Grade 11 physics and engineering lab tutor. "
            "Respond in English. Rely ONLY on the provided simulation numbers and mechanics principles; "
            "do not invent extra simulation values. Keep it concise and structured (up to 6-8 sentences).\n"
            f"Simulation data: {json.dumps(payload)}\n"
            f"Student question: {question}"
        )
        with st.spinner("Analyzing trajectory..."):
            resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        st.success("Analysis ready")
        st.write(resp.text)

st.markdown("</div>", unsafe_allow_html=True)
