import streamlit as st
import pandas as pd
import joblib
import scapy.all as scapy
import tempfile
import os

# === Config ===
MODEL_PATH = "output/iot_xgboost_model.joblib"
PROTOCOL_MAP = {6: "TCP", 17: "UDP"}

def extract_features_from_pcap(pcap_file):
    packets = scapy.rdpcap(pcap_file)
    data = []
    for pkt in packets:
        if scapy.IP in pkt:
            proto = pkt[scapy.IP].proto
            proto_name = PROTOCOL_MAP.get(proto, "OTHER")
            src_port = pkt.sport if hasattr(pkt, 'sport') else 0
            dst_port = pkt.dport if hasattr(pkt, 'dport') else 0

            data.append({
                "src_ip": pkt[scapy.IP].src,
                "dst_ip": pkt[scapy.IP].dst,
                "src_port": src_port,
                "dst_port": dst_port,
                "protocol": proto_name,
                "length": len(pkt)
            })
    return pd.DataFrame(data)

def preprocess(df):
    df = df.copy()
    df["protocol"] = df["protocol"].astype("category").cat.codes
    for col in ["src_ip", "dst_ip"]:
        df[col] = df[col].astype("category").cat.codes
    df["src_port"] = pd.to_numeric(df["src_port"], errors="coerce").fillna(0).astype(int)
    df["dst_port"] = pd.to_numeric(df["dst_port"], errors="coerce").fillna(0).astype(int)
    return df[["src_ip", "dst_ip", "src_port", "dst_port", "protocol", "length"]]

# === Streamlit App ===
st.set_page_config(page_title="IoT Traffic Analyzer", layout="centered")
st.title("🔐 IoT Traffic Analyzer with AI")
st.markdown("Upload a .pcap file to analyze traffic and detect anomalies using XGBoost model.")

uploaded_file = st.file_uploader("Choose a .pcap file", type="pcap")

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    st.info("📦 Extracting features from PCAP...")
    df_features = extract_features_from_pcap(tmp_path)
    st.success(f"✅ Extracted {len(df_features)} packets.")

    st.dataframe(df_features.head())

    st.info("🤖 Loading model and predicting...")
    model = joblib.load(MODEL_PATH)
    X = preprocess(df_features)
    preds = model.predict(X)

    df_features["prediction"] = preds
    df_features["prediction"] = df_features["prediction"].map({0: "✅ normal", 1: "🚨 anomal"})

    st.success("✅ Prediction complete.")
    st.dataframe(df_features)

    st.markdown("### 📊 Anomaly Summary")
    st.write(df_features["prediction"].value_counts())

    # Optional: download results
    csv = df_features.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download results as CSV",
        data=csv,
        file_name="iot_traffic_analysis.csv",
        mime="text/csv"
    )

    # Cleanup
    os.remove(tmp_path)