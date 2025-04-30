import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc, precision_recall_curve
from xgboost import plot_importance
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split


# === Config ===
DATASET_PATH = "output/iot_ml_dataset.csv"
MODEL_PATH = "output/iot_xgboost_model.joblib"
EXPORT_DIR = "output/"

# === Load data ===
df = pd.read_csv(DATASET_PATH)
model = joblib.load(MODEL_PATH)

# === Preprocess ===
le_protocol = LabelEncoder()
df["protocol"] = le_protocol.fit_transform(df["protocol"])

for col in ["src_ip", "dst_ip"]:
    df[col] = df[col].astype("category").cat.codes

df["src_port"] = pd.to_numeric(df["src_port"], errors="coerce").fillna(0).astype(int)
df["dst_port"] = pd.to_numeric(df["dst_port"], errors="coerce").fillna(0).astype(int)

X = df[["src_ip", "dst_ip", "src_port", "dst_port", "protocol", "length"]]
y = df["label"].map({"normal": 0, "anomal": 1})

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# === Predict ===
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

# === Confusion Matrix ===
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap="Reds", xticklabels=["Normal", "Anomal"], yticklabels=["Normal", "Anomal"])
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.savefig(EXPORT_DIR + "confusion_matrix.png")
plt.close()

# === Classification Report ===
report = classification_report(y_test, y_pred, target_names=["Normal", "Anomal"], output_dict=True)
report_df = pd.DataFrame(report).transpose()
report_df.to_csv(EXPORT_DIR + "classification_report.csv")

# === Feature Importance ===
plt.figure(figsize=(8, 6))
plot_importance(model, max_num_features=10, importance_type='weight')
plt.title("Feature Importance (Top 10)")
plt.tight_layout()
plt.savefig(EXPORT_DIR + "feature_importance.png")
plt.close()

# === ROC Curve ===
fpr, tpr, _ = roc_curve(y_test, y_proba)
roc_auc = auc(fpr, tpr)
plt.figure(figsize=(6, 5))
plt.plot(fpr, tpr, color="darkorange", lw=2, label=f"AUC = {roc_auc:.2f}")
plt.plot([0, 1], [0, 1], color="navy", lw=1, linestyle="--")
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig(EXPORT_DIR + "roc_curve.png")
plt.close()

# === Precision-Recall Curve ===
precision, recall, _ = precision_recall_curve(y_test, y_proba)
plt.figure(figsize=(6, 5))
plt.plot(recall, precision, color="green", lw=2)
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision-Recall Curve")
plt.tight_layout()
plt.savefig(EXPORT_DIR + "precision_recall_curve.png")
plt.close()


print("✅ Toate graficele au fost generate în folderul 'output/'. Include-le în raport ca un profesionist!")
