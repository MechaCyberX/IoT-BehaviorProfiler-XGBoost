import joblib
from scapy.all import sniff, IP, TCP, UDP
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

# === Config ===
MODEL_PATH = "output/iot_xgboost_model.joblib"
LOG_FILE = "output/alerts_live.log"
MAX_PACKETS = 0  # 0 = infinite
INTERFACE = None  # None = default

# === Load model ===
model = joblib.load(MODEL_PATH)
print("✅ Model loaded!")

# === Protocol encoder ===
proto_encoder = LabelEncoder()
proto_encoder.fit(["TCP", "UDP", "OTHER"])

ip_map = {}
ip_counter = 0

def encode_ip(ip):
    global ip_map, ip_counter
    if ip not in ip_map:
        ip_map[ip] = ip_counter
        ip_counter += 1
    return ip_map[ip]

def log_alert(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def process_packet(pkt):
    if IP not in pkt:
        return

    proto = "OTHER"
    src_port = dst_port = 0
    if TCP in pkt:
        proto = "TCP"
        src_port = pkt[TCP].sport
        dst_port = pkt[TCP].dport
    elif UDP in pkt:
        proto = "UDP"
        src_port = pkt[UDP].sport
        dst_port = pkt[UDP].dport

    src_ip_enc = encode_ip(pkt[IP].src)
    dst_ip_enc = encode_ip(pkt[IP].dst)
    proto_enc = proto_encoder.transform([proto])[0]

    features = pd.DataFrame([{
        "src_ip": src_ip_enc,
        "dst_ip": dst_ip_enc,
        "src_port": src_port,
        "dst_port": dst_port,
        "protocol": proto_enc,
        "length": len(pkt)
    }])

    prediction = model.predict(features)[0]

    if prediction == 1:
        alert_msg = f"🚨 ANOMALY DETECTED! {pkt[IP].src} → {pkt[IP].dst}:{dst_port} | Proto: {proto} | Len: {len(pkt)}"
        print("\n" + alert_msg)
        log_alert(alert_msg)

# === Start sniffing ===
print("📡 Listening for traffic... (Press CTRL+C to stop)")
sniff(prn=process_packet, store=False, count=MAX_PACKETS, iface=INTERFACE)
