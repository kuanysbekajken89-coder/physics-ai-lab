import os
import json
import plotly.graph_objects as go
import streamlit as st
from google import genai

from ballistics_model import get_flight_summary, simulate_flight

st.set_page_config(page_title="AI Лаборатория — Физика 11 класс", layout="wide")
st.title("AI Онлайн-Лаборатория: Полёт с сопротивлением воздуха")

st.sidebar.header("Параметры запуска")
v0 = st.sidebar.slider("Скорость v₀ (м/с)", 5.0, 80.0, 30.0, 1.0)
angle_deg = st.sidebar.slider("Угол запуска α (град)", 5.0, 85.0, 45.0, 1.0)
mass_kg = st.sidebar.slider("Масса m (кг)", 0.2, 20.0, 2.0, 0.2)
cd = st.sidebar.slider("Коэффициент формы C_d", 0.05, 1.2, 0.47, 0.01)
area_m2 = st.sidebar.slider("Площадь сечения A (м²)", 0.005, 0.2, 0.02, 0.005)

df = simulate_flight(v0, angle_deg, mass_kg, area_m2=area_m2, cd=cd)
summary = get_flight_summary(df, v0, angle_deg, mass_kg, cd)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Дальность", f"{summary['range_m']} м")
c2.metric("Макс. высота", f"{summary['max_height_m']} м")
c3.metric("Время полёта", f"{summary['flight_time_s']} с")
c4.metric("Скорость у земли", f"{summary['impact_speed_ms']} м/с")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["x_m"], y=df["y_m"], mode="lines", name="Траектория"))
fig.update_layout(xaxis_title="Дальность x (м)", yaxis_title="Высота y (м)", height=400)
st.plotly_chart(fig, use_container_width=True)

st.subheader("AI-разбор эксперимента")
question = st.text_input("Задай вопрос по графику", "Почему дальность меньше, чем в идеальной задаче без воздуха?")

if st.button("Спросить AI-наставника"):
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.warning("Добавь GEMINI_API_KEY в Secrets приложения, чтобы включить AI-ответы.")
    else:
        client = genai.Client(api_key=api_key)
        prompt = (
            "Ты наставник по физике для 11 класса. Отвечай кратко и понятно, "
            "опираясь только на данные расчёта и законы физики:\n"
            f"{json.dumps(summary, ensure_ascii=False)}\n"
            f"Вопрос: {question}"
        )
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        st.write(resp.text)
