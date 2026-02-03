import pandas as pd

alerts_path = "data/csv/kerala_deforestation_alerts_live.csv"
df = pd.read_csv(alerts_path)

print("Columns:", list(df.columns))
print("Rows:", len(df))

if df.empty:
    print("✅ No deforestation alerts this month.")
else:
    print(f"🚨 {len(df)} alert points detected.")
    print(df.head(5))
