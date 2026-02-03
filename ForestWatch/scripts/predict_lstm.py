# ============================
# ForestWatch LSTM Prediction Script
# ============================

# Import core libraries
import numpy as np           # For handling arrays and reshaping input data
import joblib                # For loading the saved scaler
from keras.models import load_model   # For loading the trained LSTM model

# ----------------------------
# STEP 1: Load the trained model and scaler
# ----------------------------
# Load the LSTM model you trained earlier (saved as forestwatch_lstm.h5).
model = load_model("models/forestwatch_lstm.h5")

# Load the scaler you saved during training (ts_scaler.pkl).
# This ensures new data is scaled in the same way as training data.
scaler = joblib.load("models/ts_scaler.pkl")

# ----------------------------
# STEP 2: Prepare input data
# ----------------------------
import pandas as pd

# Load your CSV file
df = pd.read_csv("data/csv/kerala_ndvi_nbr_monthly.csv")

# Take the last 12 months of NDVI and NBR values
sample = df[["NDVI", "NBR"]].values[-12:]


# ----------------------------
# STEP 3: Scale the input data
# ----------------------------
# Apply the same scaling transformation used during training.
sample_scaled = scaler.transform(sample)

# Reshape the data to match LSTM input format:
# (samples, sequence_length, features) → here (1, 12, 2)
sample_scaled = sample_scaled[np.newaxis, ...]

# ----------------------------
# STEP 4: Make prediction
# ----------------------------
# Use the trained model to predict risk for the next month.
pred = model.predict(sample_scaled)

# ----------------------------
# STEP 5: Display result
# ----------------------------
# Convert prediction to a float and print it.The output is a risk score proxy (based on NDVI drop).
# Closer to 1.0 → higher risk (vegetation health declining).
# Closer to 0.0 → lower risk (vegetation stable/healthy).
print("Predicted risk for next month:", float(pred.squeeze()))

import matplotlib.pyplot as plt

# Plot NDVI and NBR sequence
plt.figure(figsize=(8,4))
plt.plot(sample[:,0], marker='o', label="NDVI")
plt.plot(sample[:,1], marker='o', label="NBR")

# Add predicted risk as a horizontal line
plt.axhline(y=float(pred.squeeze()), color='red', linestyle='--', label="Predicted Risk")

plt.title("NDVI/NBR vs Predicted Risk")
plt.xlabel("Month")
plt.ylabel("Index / Risk")
plt.legend()
plt.grid(True)
plt.show()
