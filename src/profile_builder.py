import pandas as pd
import json

INPUT_CSV = "output/iot_traffic_features.csv"
OUTPUT_JSON = "output/profiles/iot_whitelist_profile.json"

def build_whitelist(csv_path):
    df = pd.read_csv(csv_path)

    profile = {}

    # Grupăm după IP sursă (dispozitive IoT)
    for device_ip, group in df.groupby("src_ip"):
        profile[str(device_ip)] = {
            "allowed_dst_ips": list(map(str, group["dst_ip"].unique())),
            "allowed_dst_ports": list(map(int, group["dst_port"].dropna().unique())),
            "allowed_protocols": list(map(str, group["protocol"].unique())),
            "avg_packet_size": float(group["length"].mean())
        }


    return profile

if __name__ == "__main__":
    profile = build_whitelist(INPUT_CSV)

    # Salvăm profilul în JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump(profile, f, indent=4)

    print(f"✅ Whitelist profile salvat în {OUTPUT_JSON}")
