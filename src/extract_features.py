from scapy.all import rdpcap, IP, TCP, UDP
import pandas as pd

# Fișierul PCAP de intrare
PCAP_FILE = "data/iot_traffic.pcap"
OUTPUT_CSV = "output/iot_traffic_features.csv"

def extract_features_scapy(pcap_file):
    packets = rdpcap(pcap_file)
    rows = []

    for pkt in packets:
        if IP in pkt:
            ip_layer = pkt[IP]
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

            rows.append({
                "timestamp": pkt.time,
                "src_ip": ip_layer.src,
                "dst_ip": ip_layer.dst,
                "protocol": proto,
                "src_port": src_port,
                "dst_port": dst_port,
                "length": len(pkt)
            })

    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    df = extract_features_scapy(PCAP_FILE)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Features extracted and saved to {OUTPUT_CSV}")
