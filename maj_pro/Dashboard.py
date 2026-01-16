import ee
import streamlit as st

# Always initialize with your project ID
ee.Initialize(project='majorpro-484507')

st.title("🌳 ForestWatch Live Alerts")
#st.success("✅ Earth Engine connected to MajorPRO project")
# 1) After detection, you have: loss_polygons (GeoJSON), metrics per polygon
event = {
    "id": "FW-KL-2026-0116-A",
    "centroid": (11.715, 76.123),
    "area_ha": 12.4,
    "ndvi_drop": -0.18,
    "nbr": 0.17,
    "confidence": "high",
    "district": "Wayanad",
    "range": "Thirunelli"
}

# 2) Contact directory (example)
contacts = {
    ("Wayanad", "Thirunelli"): {
        "email": "thirunelli.range@keralaforest.gov.in",
        "sms": "+91XXXXXXXXXX",
        "webhook": "https://gov.example.in/alerts"
    }
}

# 3) Compose alert
def compose_alert(e):
    return f"""Deforestation alert — {e['range']} Range ({e['confidence']})
When: 2026-01-16 17:40 IST
Where: {e['centroid'][0]:.3f}N, {e['centroid'][1]:.3f}E
Area affected: {e['area_ha']:.1f} ha
Evidence: NDVI drop {e['ndvi_drop']:.2f}, NBR {e['nbr']:.2f}
Map: http://localhost:8501/?center={e['centroid'][0]},{e['centroid'][1]}
Incident ID: {e['id']}
Action: Field verification within 24–48 hours recommended.
"""

# 4) Dispatch (pseudo)
def send_email(to, body): ...
def send_sms(to, body): ...
def send_webhook(url, payload): ...

c = contacts[(event["district"], event["range"])]
msg = compose_alert(event)
send_email(c["email"], msg)
send_sms(c["sms"], msg)
send_webhook(c["webhook"], event)
