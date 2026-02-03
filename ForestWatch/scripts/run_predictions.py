import pandas as pd
import numpy as np
from keras.models import load_model

# Paths
CSV_PATH = "data/csv/kerala_ndvi_nbr_monthly.csv"
MODEL_PATH = "models/forestwatch_lstm.h5"

# Step 1: Load monthly NDVI/NBR data
df = pd.read_csv(CSV_PATH)
print("Data loaded:", df.shape)
print(df.head())

# Step 2: Prepare features (NDVI + NBR)
X = df[["NDVI", "NBR"]].values
X = np.expand_dims(X, axis=0)  # shape (1, timesteps, features)

# Step 3: Load trained LSTM model
model = load_model(MODEL_PATH)

# Step 4: Run prediction
y_pred = model.predict(X)
print("Predicted risk scores:", y_pred)
