# IoT Behavior Profiler

Every device has habits. This project learns a baseline per IoT device (who it talks to, on
which ports and protocols, with what packet sizes), flags traffic that breaks it, and adds an
XGBoost stage on top. Built with Scapy, pandas, XGBoost and Streamlit. M.Sc. project, 2025.

The most useful part turned out to be what went wrong. See [What I'd fix next](#what-id-fix-next).

## How it works

Run everything from the repository root, in this order:

| Step | Command | Output |
| --- | --- | --- |
| 1. Generate traffic | `python src/generate_IoT_traffic.py` | `data/iot_traffic.pcap` |
| 2. Extract features | `python src/extract_features.py` | `output/iot_traffic_features.csv` |
| 3. Build the baselines | `python src/profile_builder.py` | `output/profiles/iot_whitelist_profile.json` |
| 4. Detect | `python src/detector.py` | `output/alerts.log` |
| 5. Label a dataset | `python prepare_ml_dataset.py` | `output/iot_ml_dataset.csv` |
| 6. Train XGBoost | `python src/train_model.py` | `output/iot_xgboost_model.joblib` |
| 7. Charts | `python src/generate_ml_analysis.py` | confusion matrix, ROC, precision-recall, feature importance |
| 8. Metrics | `python evaluate_model.py` | accuracy, precision, recall, F1 |

- **The traffic** (step 1) is synthetic, made with Scapy: ten simulated devices talking
  HTTP, HTTPS, MQTT, CoAP and DNS to three servers, plus four attacks: data exfiltration to
  suspicious IPs on 4444/TCP, a port scan, a UDP flood, and Tor-like connections on 9001.
- **The baseline** (step 3) records, per device, the destinations, ports and protocols it
  uses and its average packet size.
- **The detector** (step 4) flags a packet that goes somewhere new, uses a new port or
  protocol, or is more than 80% off the device's average size.

There are also three front ends:

```bash
sudo python live_monitor_gui.py        # score live traffic from your network interface
streamlit run streamlit_live_view.py   # watch the live alerts
streamlit run post_factum_gui.py       # upload a .pcap and score it
```

## Install

```bash
git clone https://github.com/MechaCyberX/IoT-BehaviorProfiler-XGBoost.git
cd IoT-BehaviorProfiler-XGBoost
pip install -r requirements.txt
```

## Results

XGBoost agrees with the detector's labels 98.2% of the time on a held-out 25% (170 packets):
96.3% precision and 92.9% recall on the anomalous class. Read the next section before reading
anything into that number.

## What I'd fix next

Re-reading the pipeline, four things stand out:

1. **The baseline learned the attacks.** Each device's baseline is built from the same capture
   that contains the attacks, so the suspicious IPs and ports 4444 and 9001 became "normal".
   The detector ends up catching only the UDP flood, by packet size. The exfiltration, the port
   scan and the Tor-like traffic pass. **Fix:** learn the baseline from a clean capture, or a
   clean time window, then detect on new traffic.
2. **The model learns the rules, not the attacks.** Its labels come from the detector, so
   XGBoost learns to reproduce it: it leans on packet size and destination port, the flood's
   signature. The 98% measures agreement with the rules, not detection. **Fix:** label from
   ground truth. The generator creates the attacks, so it can write the true labels too.
3. **IP addresses as features, encoded two different ways.** Training numbers IPs by their
   order in the dataset; the live monitor numbers them in the order it first sees them. So,
   live, the IP features mean something else, and ordinary traffic gets flagged. **Fix:** drop
   raw IPs and use behaviour per device and time window instead: packet rates, new
   destinations, port spread.
4. **Synthetic traffic only.** The numbers say nothing about a real fleet yet. **Fix:** test
   on a public IoT dataset, and on a capture from real devices.

## License

MIT. See [LICENSE](LICENSE).
