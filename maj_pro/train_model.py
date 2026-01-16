import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Load the labeled CSV
df = pd.read_csv("kerala_ndvi_nbr_monthly_labeled.csv")

# ✅ Fix NaN values in deforestation column
df["deforestation"] = df["deforestation"].fillna("No")   # or use dropna if you prefer
# df = df.dropna(subset=["deforestation"])

# Features (NDVI, NBR)
X = df[["NDVI", "NBR"]]

# Target (deforestation Yes/No → 0/1)
y = df["deforestation"].map({"No": 0, "Yes": 1})

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Test the model
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Save the model
joblib.dump(model, "forestwatch_model.pkl")
print("✅ Model saved as forestwatch_model.pkl")
