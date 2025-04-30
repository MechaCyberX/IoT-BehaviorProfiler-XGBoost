import pandas as pd

FEATURES_FILE = "output/iot_traffic_features.csv"
ALERTS_FILE = "output/alerts.log"
OUTPUT_FILE = "output/iot_ml_dataset.csv"

def load_alerts(alerts_path):
    alerts = set()
    with open(alerts_path, "r", encoding="utf-8") as f:
        for line in f:
            # extragem formatul: [src_ip] → dst_ip:dst_port
            try:
                src_part, rest = line.strip().split("→")
                src_ip = src_part.strip().split("[")[1].split("]")[0]
                dst_ip_port = rest.strip().split(" ")[0]
                dst_ip, dst_port = dst_ip_port.split(":")
                alerts.add((src_ip.strip(), dst_ip.strip(), dst_port.strip()))
            except Exception as e:
                continue
    return alerts

def label_dataset(df, alerts):
    def get_label(row):
        key = (str(row["src_ip"]), str(row["dst_ip"]), str(row["dst_port"]))
        return "anomal" if key in alerts else "normal"
    df["label"] = df.apply(get_label, axis=1)
    return df

if __name__ == "__main__":
    print("📥 Loading data...")
    df = pd.read_csv(FEATURES_FILE)
    alerts = load_alerts(ALERTS_FILE)

    print(f"📊 {len(alerts)} alert keys loaded.")
    df_labeled = label_dataset(df, alerts)

    print(f"💾 Saving labeled dataset to {OUTPUT_FILE} ...")
    df_labeled.to_csv(OUTPUT_FILE, index=False)
    print("✅ Dataset for ML pregătit cu succes!")
