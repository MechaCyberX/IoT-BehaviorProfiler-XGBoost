# 🛡️ Behavioral Profiling App with XGBoost

[![GitHub stars](https://img.shields.io/github/stars/MechaCyberX/IoT-BehaviorProfiler-XGBoost)](https://github.com/MechaCyberX/IoT-BehaviorProfiler-XGBoost/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

A modern application for detecting anomalies in IoT network traffic using XGBoost and behavioral profiling.


## ✨ Key Features

- Real-time anomaly detection in IoT traffic
- XGBoost-based machine learning model
- Streamlit interface for post-factum analysis
- Live monitoring and alert logging
- Easy-to-use, modular codebase

## 🛠️ Technologies Used

- Python 3.8+
- Scapy (packet capture and parsing)
- XGBoost (machine learning)
- Streamlit (web interface)
- scikit-learn (preprocessing, metrics)
- Pandas, NumPy, Matplotlib, Altair

## ⚙️ Installation
```
git clone https://github.com/MechaCyberX/behavioral-profiling-xgboost.git
cd behavioral-profiling-xgboost
pip install -r requirements.txt
```

## 🚀 Usage

### Prepare the ML Dataset
```
python src/prepare_ml_dataset.py
```
### Train the Model
```
python src/train_model.py
```
### Live Monitoring
```
python src/live_monitor_gui.py
```

### Real-Time Alert Viewer (Streamlit)
```
streamlit run src/streamlit_live_view.py
```

### Post-Factum PCAP Analysis (Streamlit)

```
streamlit run src/post_factum_gui.py
```

## 📂 Project Structure

├── src/
│ ├── prepare_ml_dataset.py
│ ├── live_monitor_gui.py
│ ├── post_factum_gui.py
│ ├── streamlit_live_view.py
│ └── ...
├── output/
├── screenshots/
├── requirements.txt
├── LICENSE
└── README.md

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork this repository
2. Create a new branch
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

*Developed with ❤️ for the IoT and cybersecurity community.*


