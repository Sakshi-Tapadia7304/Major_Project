import pandas as pd
import numpy as np
import joblib
from keras.models import Sequential
from keras.layers import LSTM, Dense


from sklearn.preprocessing import StandardScaler

#Load your CSV -> Now df holds your NDVI and NBR values.
df = pd.read_csv("data/csv/kerala_ndvi_nbr_monthly.csv")

#This takes only the NDVI and NBR numbers.We don’t need the date column for training.
series = df[["NDVI","NBR"]].values

# This makes the numbers easier for the LSTM to learn.
scaler = StandardScaler()
series_scaled = scaler.fit_transform(series)
joblib.dump(scaler, "models/ts_scaler.pkl")

#Build sequences
# This means
# Look at 12 months of NDVI/NBR. Predict the risk for the next month.
# If NDVI goes down, risk goes up.
SEQ = 12
X, y = [], []
for i in range(len(series_scaled) - SEQ):
    X.append(series_scaled[i:i+SEQ])
    y.append(1.0 - series_scaled[i+SEQ][0])  # proxy target
X, y = np.array(X), np.array(y)

#Build the LSTM model
# This is your LSTM brain:
# First layer: LSTM with 64 memory cells.
# Second layer: Dense (hidden).
# Last layer: Dense (output) → gives risk score between 0 and 1
model = Sequential([
    LSTM(64, input_shape=(SEQ, 2)),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')
])

#Compile the model-> This sets how the model learns.
# Optimizer = Adam (smart learning).
# Loss = MSE (mean squared error).
model.compile(optimizer='adam', loss='mse')

#Train the model-> This teaches the model:
# 40 rounds of learning.
# 16 samples at a time.
# 20% of data kept aside for testing.
model.fit(X, y, epochs=40, batch_size=16, validation_split=0.2)

model.save("models/forestwatch_lstm.h5")
print("✅ LSTM saved")
