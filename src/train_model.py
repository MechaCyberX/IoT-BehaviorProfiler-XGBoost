import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder
import joblib

DATASET = "output/iot_ml_dataset.csv"
MODEL_PATH = "output/iot_xgboost_model.joblib"

def preprocess(df):
    le_protocol = LabelEncoder()
    df["protocol"] = le_protocol.fit_transform(df["protocol"])

    # Encodăm IP-urile ca numerice (simplu pentru demo, se poate îmbunătăți)
    for col in ["src_ip", "dst_ip"]:
        df[col] = df[col].astype("category").cat.codes

    df["src_port"] = pd.to_numeric(df["src_port"], errors="coerce").fillna(0).astype(int)
    df["dst_port"] = pd.to_numeric(df["dst_port"], errors="coerce").fillna(0).astype(int)

    X = df[["src_ip", "dst_ip", "src_port", "dst_port", "protocol", "length"]]
    y = df["label"].map({"normal": 0, "anomal": 1})

    return X, y

if __name__ == "__main__":
    df = pd.read_csv(DATASET)
    X, y = preprocess(df)

    print("📊 Train/Test split...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    print("🚀 Training XGBoost model...")
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    model.fit(X_train, y_train)

    print("📈 Evaluating model...")
    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Precision:", precision_score(y_test, y_pred))
    print("Recall:", recall_score(y_test, y_pred))
    print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    print(f"💾 Saving model to {MODEL_PATH}")
    joblib.dump(model, MODEL_PATH)
    print("✅ Model saved!")
