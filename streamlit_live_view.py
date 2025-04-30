import streamlit as st
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt

LOG_FILE = "output/alerts_live.log"
REFRESH_INTERVAL = 5  # secunde

st.set_page_config(page_title="📡 Live Alerts", layout="wide")
st.title("🚨 Real-Time Anomaly Detection Viewer")
st.markdown("Logul este actualizat automat la fiecare câteva secunde. Poți lăsa această pagină deschisă pentru monitorizare live.")

st.divider()

# === Layout ===
col1, col2, col3 = st.columns([2, 1, 1])

placeholder = col1.empty()
chart_placeholder = col2.empty()
top_ips_placeholder = col3.empty()

custom_alert_style = """
<style>
.alert-box {
    padding: 0.9rem 1rem;
    margin-bottom: 0.6rem;
    background: linear-gradient(to right, #ff4e50, #f9d423);
    color: white;
    border-left: 6px solid #ffffff;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}
</style>
"""
st.markdown(custom_alert_style, unsafe_allow_html=True)

counter_placeholder = st.empty()
st.markdown("---")

def parse_alert_line(line):
    try:
        time_part, content = line.strip().split("] ", 1)
        timestamp = datetime.strptime(time_part.strip("["), "%Y-%m-%d %H:%M:%S")
        src_ip = content.split(" ")[3]
        return timestamp, src_ip
    except:
        return None, None

if not Path(LOG_FILE).exists():
    st.warning("⚠️ Logul de alertă nu a fost generat încă. Rulează live_monitor.py!")
else:
    last_read = 0
    timestamps = []
    sources = []

    while True:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            new_lines = lines[last_read:]
            last_read = len(lines)

        with placeholder.container():
            st.subheader("📋 Ultimele alerte în rețea")
            for line in reversed(new_lines[-20:]):
                if "🚨" in line:
                    st.markdown(f'<div class="alert-box">{line.strip()}</div>', unsafe_allow_html=True)
                else:
                    st.code(line.strip())

        for line in new_lines:
            ts, src = parse_alert_line(line)
            if ts and src:
                timestamps.append(ts)
                sources.append(src)

        # === Display alert frequency chart ===
        if timestamps:
            df = pd.DataFrame({"timestamp": timestamps, "source": sources})
            df["minute_full"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

            chart = alt.Chart(df).mark_line(interpolate="step-after", point=True, color="#ff4e50").encode(
                x=alt.X('minute_full:T', title='Timp', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('count():Q', title='Alerte'),
                tooltip=['minute_full:T', 'count()']
            ).properties(
                title="📈 Număr alerte în timp",
                width=400,
                height=250
            )
            chart_placeholder.altair_chart(chart, use_container_width=True)

            # === Counter total ===
            counter_placeholder.metric("🔢 Total alerte detectate", f"{len(df)}")

            # === Top 5 IP-uri suspecte ===
            top_ips = df["source"].value_counts().head(5).reset_index()
            top_ips.columns = ["IP", "Alerte"]
            top_ips_placeholder.subheader("📌 Top 5 IP-uri suspecte")
            top_ips_placeholder.dataframe(top_ips, use_container_width=True)

        time.sleep(REFRESH_INTERVAL)
