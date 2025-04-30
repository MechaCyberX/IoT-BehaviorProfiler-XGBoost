from scapy.all import rdpcap, IP, TCP, UDP
import json

PCAP_FILE = "data/iot_traffic.pcap"
WHITELIST_FILE = "output/profiles/iot_whitelist_profile.json"
ALERT_LOG = "output/alerts.log"

def load_whitelist(path):
    with open(path, "r") as f:
        return json.load(f)

def analyze_packet(pkt, whitelist):
    if IP not in pkt:
        return None  # ignorăm non-IP

    src_ip = pkt[IP].src
    dst_ip = pkt[IP].dst
    length = len(pkt)

    proto = "OTHER"
    src_port = dst_port = "-"
    if TCP in pkt:
        proto = "TCP"
        src_port = pkt[TCP].sport
        dst_port = pkt[TCP].dport
    elif UDP in pkt:
        proto = "UDP"
        src_port = pkt[UDP].sport
        dst_port = pkt[UDP].dport

    # Dacă IP-ul sursă nu e în whitelist => skip
    if src_ip not in whitelist:
        return f"[UNKNOWN DEVICE] {src_ip} attempted traffic"

    device_profile = whitelist[src_ip]

    alerts = []

    if dst_ip not in device_profile["allowed_dst_ips"]:
        alerts.append(f"❌ Destination IP {dst_ip} not in whitelist")

    if str(dst_port) not in map(str, device_profile["allowed_dst_ports"]):
        alerts.append(f"❌ Port {dst_port} is not whitelisted")

    if proto not in device_profile["allowed_protocols"]:
        alerts.append(f"❌ Protocol {proto} not whitelisted")

    avg_len = device_profile["avg_packet_size"]
    if abs(length - avg_len) > avg_len * 0.8:
        alerts.append(f"❌ Abnormal packet size: {length} bytes")

    if alerts:
        alert = f"[{src_ip}] → {dst_ip}:{dst_port} ({proto}) | " + " | ".join(alerts)
        return alert
    return None

def main():
    whitelist = load_whitelist(WHITELIST_FILE)
    packets = rdpcap(PCAP_FILE)

    with open(ALERT_LOG, "w", encoding="utf-8") as log:
        for pkt in packets:
            alert = analyze_packet(pkt, whitelist)
            if alert:
                print("🚨", alert)
                log.write(alert + "\n")

    print(f"✅ Analiza completă. Vezi alerta în {ALERT_LOG}")

if __name__ == "__main__":
    main()
