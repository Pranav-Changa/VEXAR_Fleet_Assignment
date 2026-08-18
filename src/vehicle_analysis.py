import pandas as pd
import numpy as np

# ============================================================
# LOAD MASTER DATA
# ============================================================

master = pd.read_csv("outputs/master_telemetry.csv")

master["Trip_Date"] = pd.to_datetime(master["Trip_Date"])
master["Last_Service_Date"] = pd.to_datetime(
    master["Last_Service_Date"]
)

# ============================================================
# CREATE SENSOR FEATURES
# ============================================================

# Deviation of vertical acceleration from expected gravity
master["Z_Deviation"] = (
    master["Accel_Z_g"] - 1.0
).abs()

# Gyroscope magnitude
master["Gyro_Magnitude"] = np.sqrt(
    master["Gyro_X_dps"] ** 2
    + master["Gyro_Y_dps"] ** 2
    + master["Gyro_Z_dps"] ** 2
)


# ============================================================
# DEFINE VEHICLE SENSOR ANOMALIES
# ============================================================

# Vibration anomaly
master["Vibration_Anomaly"] = (
    master["Z_Deviation"] > 0.15
)

# High rotational activity
master["Gyro_Anomaly"] = (
    master["Gyro_Magnitude"] > 10
)


# ============================================================
# VEHICLE-LEVEL AGGREGATION
# ============================================================

vehicle_metrics = (
    master
    .groupby("Vehicle_ID")
    .agg(

        Total_Telemetry=("Trip_ID", "size"),

        Vibration_Anomalies=(
            "Vibration_Anomaly",
            "sum"
        ),

        Gyro_Anomalies=(
            "Gyro_Anomaly",
            "sum"
        ),

        Mean_Z_Deviation=(
            "Z_Deviation",
            "mean"
        ),

        Z_Deviation_Std=(
            "Z_Deviation",
            "std"
        ),

        Gyro_Magnitude_Mean=(
            "Gyro_Magnitude",
            "mean"
        ),

        Gyro_Magnitude_Std=(
            "Gyro_Magnitude",
            "std"
        ),

        Manufacture_Year=(
            "Manufacture_Year",
            "first"
        ),

        Last_Service_Date=(
            "Last_Service_Date",
            "first"
        ),

        Odometer_KM=(
            "Odometer_KM_Start_of_Week",
            "first"
        ),

        Make=(
            "Make",
            "first"
        ),

        Model=(
            "Model",
            "first"
        )
    )
    .reset_index()
)


# ============================================================
# CALCULATE ANOMALY RATES
# ============================================================

vehicle_metrics["Vibration_Anomaly_Rate"] = (
    vehicle_metrics["Vibration_Anomalies"]
    / vehicle_metrics["Total_Telemetry"]
    * 100
)

vehicle_metrics["Gyro_Anomaly_Rate"] = (
    vehicle_metrics["Gyro_Anomalies"]
    / vehicle_metrics["Total_Telemetry"]
    * 100
)


# ============================================================
# OBSERVATION PERIOD
# ============================================================

analysis_date = master["Trip_Date"].max()

vehicle_metrics["Days_Since_Last_Service"] = (
    analysis_date -
    vehicle_metrics["Last_Service_Date"]
).dt.days


# ============================================================
# VEHICLE AGE
# ============================================================

vehicle_metrics["Vehicle_Age_Years"] = (
    analysis_date.dt.year
    if hasattr(analysis_date, "dt")
    else analysis_date.year
) - vehicle_metrics["Manufacture_Year"]


# ============================================================
# CONVERT VEHICLE METRICS TO PERCENTILE SCORES
# ============================================================

vehicle_metrics["Vibration_Score"] = (
    vehicle_metrics["Vibration_Anomaly_Rate"]
    .rank(pct=True)
    * 100
)

vehicle_metrics["Gyro_Score"] = (
    vehicle_metrics["Gyro_Anomaly_Rate"]
    .rank(pct=True)
    * 100
)

vehicle_metrics["Variability_Score"] = (
    vehicle_metrics["Z_Deviation_Std"]
    .rank(pct=True)
    * 100
)


# ============================================================
# SENSOR-BASED HEALTH RISK SCORE
# ============================================================

vehicle_metrics["Health_Risk_Score"] = (

    0.45 *
    vehicle_metrics["Vibration_Score"]

    +

    0.30 *
    vehicle_metrics["Gyro_Score"]

    +

    0.25 *
    vehicle_metrics["Variability_Score"]
)


vehicle_metrics["Health_Risk_Score"] = (
    vehicle_metrics["Health_Risk_Score"]
    .round(2)
)


# ============================================================
# HEALTH CATEGORY
# ============================================================

def classify_health(score):

    if score <= 30:
        return "Healthy"

    elif score <= 60:
        return "Monitor"

    else:
        return "Maintenance Review"


vehicle_metrics["Health_Category"] = (
    vehicle_metrics["Health_Risk_Score"]
    .apply(classify_health)
)


# ============================================================
# SORT BY HEALTH RISK
# ============================================================

vehicle_metrics = vehicle_metrics.sort_values(
    "Health_Risk_Score",
    ascending=False
)


# ============================================================
# DISPLAY
# ============================================================

print("\n" + "=" * 90)
print("VEHICLE HEALTH ANALYSIS")
print("=" * 90)

display_columns = [
    "Vehicle_ID",
    "Make",
    "Model",
    "Total_Telemetry",
    "Vibration_Anomaly_Rate",
    "Gyro_Anomaly_Rate",
    "Mean_Z_Deviation",
    "Z_Deviation_Std",
    "Vehicle_Age_Years",
    "Days_Since_Last_Service",
    "Odometer_KM",
    "Health_Risk_Score",
    "Health_Category"
]

print(
    vehicle_metrics[display_columns]
    .to_string(index=False)
)


# ============================================================
# CATEGORY SUMMARY
# ============================================================

print("\n" + "=" * 90)
print("HEALTH CATEGORY SUMMARY")
print("=" * 90)

print(
    vehicle_metrics["Health_Category"]
    .value_counts()
)


# ============================================================
# TOP 5 VEHICLES REQUIRING REVIEW
# ============================================================

print("\n" + "=" * 90)
print("TOP 5 VEHICLES REQUIRING MAINTENANCE REVIEW")
print("=" * 90)

print(
    vehicle_metrics[
        display_columns
    ]
    .head(5)
    .to_string(index=False)
)


# ============================================================
# TOP 5 HEALTHIEST VEHICLES
# ============================================================

print("\n" + "=" * 90)
print("TOP 5 HEALTHIEST VEHICLES")
print("=" * 90)

print(
    vehicle_metrics[
        display_columns
    ]
    .tail(5)
    .sort_values("Health_Risk_Score")
    .to_string(index=False)
)


# ============================================================
# SAVE RESULTS
# ============================================================

vehicle_metrics.to_csv(
    "outputs/vehicle_health.csv",
    index=False
)

print("\nVehicle health results saved to:")
print("outputs/vehicle_health.csv")