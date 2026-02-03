# ============================================================
# ForestWatch Dashboard
# Shows monthly NDVI/NBR trends + live deforestation alerts
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
from keras.models import load_model
import leafmap.foliumap as leafmap
import ee # earthengine 

# ------------------------------------------------------------
# STEP 0: Helper function to add Earth Engine layers to leafmap
# ------------------------------------------------------------
def add_ee_layer(self, ee_image_object, vis_params, name):
    """
    Allows leafmap to display Earth Engine raster layers.
    Converts EE image into a tile layer and adds it to the map.
    """
    try:
        map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
        self.add_tile_layer(
            url=map_id_dict['tile_fetcher'].url_format,
            name=name,
            attribution="Google Earth Engine"
        )
    except Exception as e:
        st.error(f"Could not add EE layer: {e}")

# Register the helper with leafmap
leafmap.Map.add_ee_layer = add_ee_layer

# ------------------------------------------------------------
# STEP 1: State dropdown
# ------------------------------------------------------------
state = st.selectbox("Choose State", ["Kerala", "Maharashtra", "Karnataka"])

# ------------------------------------------------------------
# STEP 2: File paths
# ------------------------------------------------------------
if state == "Kerala":
    MONTHLY_CSV = "data/csv/kerala_ndvi_nbr_monthly.csv"
    ALERTS_CSV = "data/csv/kerala_deforestation_alerts.csv"
elif state == "Maharashtra":
    MONTHLY_CSV = "data/csv/maharashtra_ndvi_nbr_monthly.csv"
    ALERTS_CSV = "data/csv/maharashtra_deforestation_alerts.csv"
elif state == "Karnataka":
    MONTHLY_CSV = "data/csv/karnataka_ndvi_nbr_monthly.csv"
    ALERTS_CSV = "data/csv/karnataka_deforestation_alerts.csv"

MODEL_PATH = "models/forestwatch_lstm.h5"

# ------------------------------------------------------------
# STEP 3: Title
# ------------------------------------------------------------
st.title("🌱 ForestWatch Dashboard")

# ------------------------------------------------------------
# STEP 4: Load data safely
# ------------------------------------------------------------
try:
    monthly = pd.read_csv(MONTHLY_CSV)
except Exception:
    monthly = pd.DataFrame()
    st.error("Monthly NDVI/NBR CSV not found. Please export from Earth Engine.")

try:
    alerts = pd.read_csv(ALERTS_CSV)
except Exception:
    alerts = pd.DataFrame()
    st.error("Alerts CSV not found. Please export from Earth Engine.")

# --- STEP 4b: Filter out dummy safeguard rows ---
# If the alerts CSV contains the dummy safeguard row with "note = No alerts this month",
# we drop it so the dashboard never shows false alert points.

if 'note' in alerts.columns:
    alerts = alerts[alerts['note'] != 'No alerts this month']

# ------------------------------------------------------------
# STEP 5: Run LSTM model for risk score
# ------------------------------------------------------------
if not monthly.empty and len(monthly) >= 12:
    # Take last 12 months of NDVI/NBR values
    X = monthly[["NDVI","NBR"]].values[-12:]
    X = np.expand_dims(X, axis=0)

    # Load trained LSTM model
    model = load_model(MODEL_PATH)

    # Predict risk score
    risk_score = model.predict(X)[0][0]
    st.metric("Predicted Risk Score", f"{risk_score:.2f}")
else:
    risk_score = 0.0
    st.warning("Not enough monthly data to compute risk score.")

# ------------------------------------------------------------
# STEP 6: Alerts summary
# ------------------------------------------------------------
if alerts.empty:
    st.success(f"✅ No deforestation alerts in {state} this month.")
else:
    total_points = len(alerts)
    st.metric("Total Points Flagged", total_points)

    # --- District summary ---
    # If the alerts CSV has a 'district' column (added in Earth Engine),
    # show a breakdown of how many alerts occurred in each district.
    if 'district' in alerts.columns:
        district_summary = alerts['district'].value_counts()
        st.error(f"🚨 Deforestation detected in {len(district_summary)} districts of {state}!")
        st.table(district_summary)

# ------------------------------------------------------------
# STEP 7: Unified Map (forest density + alerts overlay)
# ------------------------------------------------------------
st.subheader("🌍 Forest Density + Alerts Map")

# Only proceed if alerts CSV has lat/long columns
if {'latitude','longitude'}.issubset(alerts.columns):
    # Initialize Earth Engine
    ee.Initialize(project='majorpro-484507')

    # Center map depending on state
    center_coords = [10.85, 76.27] if state == "Kerala" else [19.75, 75.71]
    m = leafmap.Map(center=center_coords, zoom=7)

    # --------------------------------------------------------
    # Add a basemap with place names (towns, roads, labels)
    # --------------------------------------------------------
    m.add_basemap("OpenStreetMap")

    # --------------------------------------------------------
    # Forest density raster (Hansen treecover2000)
    # This is an ee.Image, so we use add_ee_layer
    # --------------------------------------------------------
    hansen = ee.Image("UMD/hansen/global_forest_change_2022_v1_10")
    treecover = hansen.select("treecover2000")
    vis_params = {"min": 0, "max": 100, "palette": ["#ffffcc", "#006400"]}
    m.add_ee_layer(treecover, vis_params, "Forest Density")

    # --------------------------------------------------------
    # Alerts overlay (red points from CSV lat/long)
    # --------------------------------------------------------
    m.add_points_from_xy(alerts, x="longitude", y="latitude",
                         layer_name="Deforestation Alerts", color="red")

    # --------------------------------------------------------
    # District boundaries overlay
    # NOTE: districts is a FeatureCollection, not an Image.
    # So we cannot use add_ee_layer here.
    # Instead, convert to GeoJSON and add with add_geojson.
    # --------------------------------------------------------
    districts = ee.FeatureCollection("FAO/GAUL/2015/level2") \
                    .filter(ee.Filter.eq("ADM1_NAME", state))
    m.add_geojson(districts.getInfo(), layer_name=f"{state} Districts", color="blue")

    # --------------------------------------------------------
    # Legend for map layers
    # --------------------------------------------------------
    legend_dict = {
        "Sparse Forest": "#ffffcc",
        "Dense Forest": "#006400",
        "Deforestation Alerts": "red",
        "District Boundaries": "blue"
    }
    m.add_legend(title="Legend", legend_dict=legend_dict)

    # Show map in Streamlit
    m.to_streamlit(height=600)
else:
    st.info("No latitude/longitude columns found in alerts data.")
