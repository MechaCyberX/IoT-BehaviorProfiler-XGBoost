from scapy.all import IP, TCP, UDP, Raw, wrpcap
import random

# IP-uri pentru dispozitive IoT simulate
iot_devices = [f"192.168.1.{i}" for i in range(100, 110)]
normal_servers = ["192.168.1.1", "192.168.1.2", "192.168.1.254"]
malicious_ips = ["10.10.10.10", "172.16.0.66", "185.100.87.55"]

# Protocoale legitime utilizate de IoT
protocols = [
    {"proto": TCP, "dport": 80, "desc": "HTTP"},
    {"proto": TCP, "dport": 443, "desc": "HTTPS"},
    {"proto": UDP, "dport": 1883, "desc": "MQTT"},
    {"proto": UDP, "dport": 5683, "desc": "CoAP"},
    {"proto": UDP, "dport": 53, "desc": "DNS"}
]

packets = []

# 1. Trafic normal între dispozitive și servere
for _ in range(300):
    src = random.choice(iot_devices)
    dst = random.choice(normal_servers)
    ptype = random.choice(protocols)
    payload = f"legit_{ptype['desc']}_request".encode()
    pkt = IP(src=src, dst=dst) / ptype["proto"](sport=random.randint(1024, 65535), dport=ptype["dport"]) / Raw(load=payload)
    packets.append(pkt)

# 2. Trafic anormal spre IP-uri suspecte (exfiltrare de date)
for _ in range(100):
    src = random.choice(iot_devices)
    dst = random.choice(malicious_ips)
    ptype = TCP
    payload = b"EXFIL_DATA_" + bytes(random.getrandbits(8) for _ in range(20))
    pkt = IP(src=src, dst=dst) / ptype(sport=random.randint(1024, 65535), dport=4444) / Raw(load=payload)
    packets.append(pkt)

# 3. Port scanning de la un dispozitiv compromis
scanning_device = random.choice(iot_devices)
for port in range(20, 100):
    pkt = IP(src=scanning_device, dst="192.168.1.5") / TCP(sport=random.randint(1000, 5000), dport=port, flags="S")
    packets.append(pkt)

# 4. Trafic flood (DoS-like)
for _ in range(150):
    src = random.choice(iot_devices)
    dst = random.choice(malicious_ips)
    payload = b"x" * random.randint(200, 800)
    pkt = IP(src=src, dst=dst) / UDP(sport=random.randint(1024, 65535), dport=random.randint(1024, 65535)) / Raw(load=payload)
    packets.append(pkt)

# 5. Activitate suspectă: conexiuni către Tor / IP-uri ciudate
for _ in range(50):
    src = random.choice(iot_devices)
    dst = "185.220.101.1"
    pkt = IP(src=src, dst=dst) / TCP(sport=random.randint(2000, 6000), dport=9001) / Raw(load=b"tor_like_behavior")
    packets.append(pkt)

# Salvăm tot traficul într-un fișier .pcap
wrpcap("data/iot_traffic.pcap", packets)
print("✅ Fișierul pcap a fost generat: data/iot_traffic.pcap")
