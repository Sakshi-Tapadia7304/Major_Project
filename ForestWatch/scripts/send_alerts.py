import subprocess

print("Checking alerts CSV and sending SMS/email if needed...")
subprocess.run(["python", "scripts/send_alerts_sms.py"], check=False)
subprocess.run(["python", "scripts/send_alerts_email.py"], check=False)
print("Done.")
