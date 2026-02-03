import os
import smtplib
import pandas as pd
from email.mime.text import MIMEText

ALERTS_CSV = "data/csv/kerala_deforestation_alerts_live.csv"

def format_email(df):
    top = df.head(10)
    lines = [
        f"{len(df)} deforestation points flagged (NDVI < 0.3) — {df['date'].iloc[0]}",
        "",
        "Top locations:"
    ]
    for _, r in top.iterrows():
        lines.append(f"- ({r['latitude']:.4f}, {r['longitude']:.4f}) NDVI={r['NDVI']:.2f}")
    lines.append("")
    lines.append("Full dataset is in your Drive/repo.")
    return "\n".join(lines)

def send_email(body):
    sender = os.getenv("ALERT_EMAIL_FROM")
    password = os.getenv("ALERT_EMAIL_PASS")
    recipient = os.getenv("ALERT_EMAIL_TO")

    if not all([sender, password, recipient]):
        raise RuntimeError("Missing email env vars: ALERT_EMAIL_FROM, ALERT_EMAIL_PASS, ALERT_EMAIL_TO")

    msg = MIMEText(body)
    msg["Subject"] = "ForestWatch ALERT"
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, [recipient], msg.as_string())
    print("✅ Email sent.")

def main():
    df = pd.read_csv(ALERTS_CSV)
    if df.empty:
        print("✅ No deforestation alerts this month—email not sent.")
        return
    body = format_email(df)
    print("Preview Email:\n", body)
    send_email(body)

if __name__ == "__main__":
    main()
