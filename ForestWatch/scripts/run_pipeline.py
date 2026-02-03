import pandas as pd
import numpy as np
from keras.models import load_model

from send_alerts_sms import send_sms
from send_alerts_email import send_email

# Paths
MONTHLY_CSV = "data/csv/kerala_ndvi_nbr_monthly.csv"
ALERTS_CSV = "data/csv/kerala_deforestation_alerts_live.csv"
MODEL_PATH = "models/forestwatch_lstm.h5"

# Step 1: Load monthly NDVI/NBR data
monthly = pd.read_csv(MONTHLY_CSV)
#Use the last 12 months
#If your model was trained on 12‑month sequences, just take the last 12 rows:
X = monthly[["NDVI", "NBR"]].values[-12:]   # last 12 months
X = np.expand_dims(X, axis=0)               # shape (1, 12, 2)

#Create sliding windows of 12 months
#If you want predictions for multiple periods:
"""def create_windows(data, window=12):
    X = []
    for i in range(len(data) - window + 1):
        X.append(data[i:i+window])
    return np.array(X)

data = monthly[["NDVI", "NBR"]].values
X = create_windows(data, window=12)   # shape (num_samples, 12, 2)

risk_scores = model.predict(X)
print(risk_scores)"""


# Step 2: Load LSTM model and predict risk
model = load_model(MODEL_PATH)
risk_score = model.predict(X)[0][0]  # assuming single output
print("Predicted risk score:", risk_score)

# Step 3: Load alerts CSV
alerts = pd.read_csv(ALERTS_CSV)

# Step 4: Decision logic
RISK_THRESHOLD = 0.7  # adjust based on your model scale
if risk_score >= RISK_THRESHOLD and not alerts.empty:
    print("🚨 ALERT: High risk + deforestation points detected!")
    print(alerts.head(5))
    body = f"ForestWatch ALERT: Risk={risk_score:.2f}, {len(alerts)} points flagged." 
    send_sms(body) 
    send_email(body)
else:
    print("✅ No combined alert triggered.")
