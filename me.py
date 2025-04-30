import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# === Config ===
MODEL_PATH = "output/iot_xgboost_model.joblib"
DATASET_PATH = "output/iot_ml_dataset.csv"

# === Load ===
df = pd.read_csv(DATASET_PATH)
model = joblib.load(MODEL_PATH)

# === Preprocessing ===
le_protocol = LabelEncoder()
df["protocol"] = le_protocol.fit_transform(df["protocol"])

for col in ["src_ip", "dst_ip"]:
    df[col] = df[col].astype("category").cat.codes

df["src_port"] = pd.to_numeric(df["src_port"], errors="coerce").fillna(0).astype(int)
df["dst_port"] = pd.to_numeric(df["dst_port"], errors="coerce").fillna(0).astype(int)

X = df[["src_ip", "dst_ip", "src_port", "dst_port", "protocol", "length"]]
y = df["label"].map({"normal": 0, "anomal": 1})

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# === Predict & Metrics ===
y_pred = model.predict(X_test)

acc = accuracy_score(y_test, y_pred) * 100
prec = precision_score(y_test, y_pred) * 100
rec = recall_score(y_test, y_pred) * 100
f1 = f1_score(y_test, y_pred) * 100

print("\n🎯 PERFORMANȚĂ MODEL XGBOOST")
print(f"✅ Accuracy:        {acc:.2f}%")
print(f"🎯 Precision:       {prec:.2f}%")
print(f"📈 Recall:          {rec:.2f}%")
print(f"🏆 F1-score:         {f1:.2f}%")
