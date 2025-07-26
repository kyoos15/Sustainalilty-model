import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GreenPulse Dashboard", layout="centered")
st.title("🌿 GreenPulse Energy Dashboard")

# Input for building
building_id = st.text_input("Enter Building ID", "building_001")

# Button to load data
if st.button("Load Data"):
    url = f"http://localhost:8000/data/{building_id}"
    res = requests.get(url)
    data = res.json().get("data", [])

    if not data:
        st.warning("⚠️ No energy data found for this building.")
    else:
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(by="timestamp")

        fig = px.line(df, x='timestamp', y='electricity_kWh', title='Electricity Usage Over Time')
        st.plotly_chart(fig, use_container_width=True)

        # ---------- WEEKLY REPORT ----------
        st.subheader("📆 Weekly Report & Sustainability Score")
        report = requests.get(f"http://localhost:8000/weekly_report/{building_id}").json()
        if "message" in report:
            st.info(report["message"])
        else:
            st.write(f"- Total kWh: **{report['total_energy_kWh']}**")
            st.write(f"- Average kWh/day: **{report['average_energy_kWh']}**")
            st.write(f"- Sustainability Score: **{report['sustainability_score']} / 100**")

        # ---------- GAMIFICATION ----------
        st.subheader("🏆 Energy-Saving Streak")
        gamify = requests.get(f"http://localhost:8000/gamification/{building_id}").json()
        st.write(f"- Consecutive Days Below {gamify['threshold_kWh']} kWh: **{gamify['energy_saving_streak_days']} days**")

        # ---------- AI PREDICTION ----------
        st.subheader("🔮 Predicted Energy Usage (Stub)")
        pred = requests.get(f"http://localhost:8000/predict_energy/{building_id}").json()
        st.write(f"- Forecast for next usage: **{pred['predicted_next_usage_kWh']} kWh**")
        st.caption(pred["note"])

# Buttons for additional insights
if st.button("💡 Get Suggestions"):
    tips = requests.get(f"http://localhost:8000/suggestions/{building_id}").json().get("tips", [])
    for tip in tips:
        st.success(tip)

if st.button("🚨 Check Alerts"):
    alerts = requests.get(f"http://localhost:8000/alerts/{building_id}").json().get("alerts", [])
    if not alerts:
        st.info("✅ No abnormal energy spikes detected.")
    else:
        for alert in alerts:
            st.error(f"{alert['timestamp']}: {alert['alert']}")
