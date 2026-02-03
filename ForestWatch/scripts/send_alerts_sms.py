import os
import pandas as pd
from twilio.rest import Client

ALERTS_CSV = "data/csv/kerala_deforestation_alerts_live.csv"

def format_message(df):
    top = df.head(3)
    lines = [
        f"ForestWatch ALERT ({df['date'].iloc[0]}): {len(df)} points flagged (NDVI<0.3)."
    ]
    for _, r in top.iterrows():
        lines.append(f"- ({r['latitude']:.4f}, {r['longitude']:.4f}) NDVI={r['NDVI']:.2f}")
    lines.append("Check dashboard/repo for full list.")
    return "\n".join(lines)

def send_sms(body):
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    from_num = os.getenv("TWILIO_FROM")
    to_num = os.getenv("ALERT_TO")

    if not all([sid, token, from_num, to_num]):
        raise RuntimeError("Missing Twilio env vars: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, ALERT_TO")

    client = Client(sid, token)
    msg = client.messages.create(body=body, from_=from_num, to=to_num)
    print(f"✅ SMS sent: SID={msg.sid}")

def main():
    df = pd.read_csv(ALERTS_CSV)
    if df.empty:
        print("✅ No deforestation alerts this month—SMS not sent.")
        return
    body = format_message(df)
    print("Preview SMS:\n", body)
    send_sms(body)

if __name__ == "__main__":
    main()
