import os
import json
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from google import genai

from ballistics_model import get_flight_summary, simulate_flight

st.set_page_config(
    page_title="AI Лаборатория — Физика 11 класс",
    page_icon="🚀",
    layout="wide",
)

# --- Лёгкое оформление карточек и заголовка ---
st.markdown(
    """
    <style>
        .lab-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
            padding: 20px 24px;
            border-radius: 16px;
            color: #ffffff;
            margin-bottom: 18px;
        }
        .lab-header h1 {
            margin: 0 0 6px 0;
            font-size: 1.65rem;
            color: #ffffff;
        }
        .lab-header p {
            margin: 0;
            color: #cbd5e1;
            font-size: 0.95rem;
        }
        .metric-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        }
        .metric-label {
            font-size: 0.82rem;
            color: #64748b;
            margin-bottom: 4px;
        }
        .metric-value {
            font-size: 1.35rem;
            font-weight: 700;
            color: #0f172a;
        }
        .metric-sub {
            font-size: 0.78rem;
            color: #475569;
            margin-top: 2px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Значения параметров по умолчанию (в сессии, чтобы работали пресеты) ---
defaults = {
    "v0": 35.0,
    "angle_deg": 40.0,
    "mass_kg": 2.5,
    "cd": 0.30,
    "area_m2": 0.02,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def apply_preset(v0, angle_deg, mass_kg, cd, area_m2):
    st.session_state["v0"] = v0
    st.session_state["angle_deg"] = angle_deg
    st.session_state["mass_kg"] = mass_kg
    st.session_state["cd"] = cd
    st.session_state["area_m2"] = area_m2


# --- Шапка ---
st.markdown(
    """
    <div class="lab-header">
        <h1>AI Онлайн-Лаборатория: Баллистика и сопротивление воздуха</h1>
        <p>Интерактивный стенд для 11 класса — сравнивай реальную траекторию с идеальной школьной моделью без воздуха.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Быстрые сценарии ---
st.markdown("**Быстрые пресеты:**")
p1, p2, p3, p4 = st.columns(4)
with p1:
    st.button(
        "⚽ Мяч",
        use_container_width=True,
        on_click=apply_preset,
        args=(28.0, 38.0, 0.45, 0.47, 0.038),
    )
with p2:
    st.button(
        "🛸 Обтекаемый зонд",
        use_container_width=True,
        on_click=apply_preset,
        args=(45.0, 42.0, 3.0, 0.12, 0.015),
    )
with p3:
    st.button(
        "🪨 Тяжёлый камень",
        use_container_width=True,
        on_click=apply_preset,
        args=(35.0, 45.0, 8.0, 0.55, 0.02),
    )
with p4:
    st.button(
        "🔄 Сброс",
        use_container_width=True,
        on_click=apply_preset,
        args=(35.0, 40.0, 2.5, 0.30, 0.02),
    )

# --- Боковая панель с параметрами ---
st.sidebar.header("Параметры запуска")
v0 = st.sidebar.slider("Начальная скорость v₀ (м/с)", 5.0, 80.0, step=1.0, key="v0")
angle_deg = st.sidebar.slider("Угол запуска α (град)", 5.0, 85.0, step=1.0, key="angle_deg")
mass_kg = st.sidebar.slider("Масса тела m (кг)", 0.2, 20.0, step=0.1, key="mass_kg")
cd = st.sidebar.slider("Коэффициент формы C_d", 0.05, 1.2, step=0.01, key="cd")
area_m2 = st.sidebar.slider("Площадь сечения A (м²)", 0.005, 0.2, step=0.005, key="area_m2")

show_ideal = st.sidebar.checkbox("Показать траекторию без воздуха", value=True)

# --- Расчёт текущего полёта ---
df = simulate_flight(v0, angle_deg, mass_kg, area_m2=area_m2, cd=cd)
summary = get_flight_summary(df, v0, angle_deg, mass_kg, cd)

# Расчёт идеального полёта без сопротивления воздуха (g = 9.81)
g = 9.81
rad = np.radians(angle_deg)
t_ideal = (2.0 * v0 * np.sin(rad)) / g
range_ideal = round(float((v0 ** 2) * np.sin(2.0 * rad) / g), 2)
height_ideal = round(float(((v0 * np.sin(rad)) ** 2) / (2.0 * g)), 2)

t_arr = np.linspace(0.0, t_ideal, 150)
x_ideal = v0 * np.cos(rad) * t_arr
y_ideal = v0 * np.sin(rad) * t_arr - 0.5 * g * (t_arr ** 2)

diff_range = round(summary["range_m"] - range_ideal, 2)

# --- Красивые карточки метрик ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Дальность полёта</div>
            <div class="metric-value">{summary['range_m']} м</div>
            <div class="metric-sub">К идеальной: {diff_range:+.2f} м</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Макс. высота</div>
            <div class="metric-value">{summary['max_height_m']} м</div>
            <div class="metric-sub">Без воздуха: {height_ideal} м</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Время полёта</div>
            <div class="metric-value">{summary['flight_time_s']} с</div>
            <div class="metric-sub">Без воздуха: {round(float(t_ideal), 2)} с</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Скорость у земли</div>
            <div class="metric-value">{summary['impact_speed_ms']} м/с</div>
            <div class="metric-sub">Начальная: {v0} м/с</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# --- График траекторий ---
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df["x_m"],
        y=df["y_m"],
        mode="lines",
        name="С сопротивлением воздуха",
        line=dict(color="#2563eb", width=3),
    )
)

if show_ideal:
    fig.add_trace(
        go.Scatter(
            x=x_ideal,
            y=y_ideal,
            mode="lines",
            name="Без воздуха (11 класс)",
            line=dict(color="#94a3b8", width=2, dash="dash"),
        )
    )

fig.update_layout(
    template="plotly_white",
    xaxis_title="Дальность по горизонтали x (м)",
    yaxis_title="Высота y (м)",
    height=420,
    margin=dict(l=20, r=20, t=30, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig, use_container_width=True)

# --- AI-разбор эксперимента ---
st.markdown("### 🤖 AI-наставник по физике")
question = st.text_input(
    "Задай вопрос по текущему запуску",
    "Почему реальная траектория ниже пунктирной и как влияет масса?",
)

if st.button("Разобрать с AI", type="primary"):
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.warning("Добавь GEMINI_API_KEY в Secrets приложения, чтобы включить AI-ответы.")
    else:
        payload = {
            "current_with_drag": summary,
            "ideal_no_drag": {
                "range_m": range_ideal,
                "max_height_m": height_ideal,
                "flight_time_s": round(float(t_ideal), 2),
                "diff_range_m": diff_range,
            },
        }
        client = genai.Client(api_key=api_key)
        prompt = (
            "Ты дружелюбный наставник по физике для 11 класса. "
            "Отвечай структурированно, понятно и кратко (до 6-8 предложений). "
            "Опирайся ТОЛЬКО на переданные числа и законы механики:\n"
            f"{json.dumps(payload, ensure_ascii=False)}\n"
            f"Вопрос: {question}"
        )
        with st.spinner("Анализирую траекторию..."):
            resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        st.info(resp.text)
