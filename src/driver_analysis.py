import pandas as pd
import numpy as np

# ============================================================
# LOAD MASTER DATA
# ============================================================

master = pd.read_csv("outputs/master_telemetry.csv")

# ============================================================
# DEFINE RISK EVENTS
# ============================================================

# Speeding
master["Speeding_Event"] = (
    master["Speed_kmph"] > 50
)

# Harsh acceleration
master["Harsh_Acceleration_Event"] = (
    master["Accel_X_g"] > 0.35
)

# Harsh braking
master["Harsh_Braking_Event"] = (
    master["Accel_X_g"] < -0.35
)

# Lateral movement
master["Lateral_Event"] = (
    master["Accel_Y_g"].abs() > 0.25
)

# Gyroscope magnitude
master["Gyro_Magnitude"] = np.sqrt(
    master["Gyro_X_dps"] ** 2
    + master["Gyro_Y_dps"] ** 2
    + master["Gyro_Z_dps"] ** 2
)

# High rotational movement
master["High_Gyro_Event"] = (
    master["Gyro_Magnitude"] > 10
)


# ============================================================
# DRIVER-LEVEL AGGREGATION
# ============================================================

driver_metrics = (
    master
    .groupby(["Driver_ID", "Driver_Name"])
    .agg(
        Total_Telemetry=("Trip_ID", "size"),

        Speeding_Events=("Speeding_Event", "sum"),

        Harsh_Acceleration_Events=(
            "Harsh_Acceleration_Event",
            "sum"
        ),

        Harsh_Braking_Events=(
            "Harsh_Braking_Event",
            "sum"
        ),

        Lateral_Events=(
            "Lateral_Event",
            "sum"
        ),

        High_Gyro_Events=(
            "High_Gyro_Event",
            "sum"
        )
    )
    .reset_index()
)


# ============================================================
# CALCULATE EVENT RATES
# ============================================================

driver_metrics["Speeding_Rate"] = (
    driver_metrics["Speeding_Events"]
    / driver_metrics["Total_Telemetry"]
    * 100
)

driver_metrics["Harsh_Acceleration_Rate"] = (
    driver_metrics["Harsh_Acceleration_Events"]
    / driver_metrics["Total_Telemetry"]
    * 100
)

driver_metrics["Harsh_Braking_Rate"] = (
    driver_metrics["Harsh_Braking_Events"]
    / driver_metrics["Total_Telemetry"]
    * 100
)

driver_metrics["Lateral_Event_Rate"] = (
    driver_metrics["Lateral_Events"]
    / driver_metrics["Total_Telemetry"]
    * 100
)

driver_metrics["High_Gyro_Rate"] = (
    driver_metrics["High_Gyro_Events"]
    / driver_metrics["Total_Telemetry"]
    * 100
)


# ============================================================
# CONVERT RATES INTO FLEET-RELATIVE PERCENTILE SCORES
# ============================================================

risk_metrics = [
    "Speeding_Rate",
    "Harsh_Acceleration_Rate",
    "Harsh_Braking_Rate",
    "Lateral_Event_Rate",
    "High_Gyro_Rate"
]

for metric in risk_metrics:

    driver_metrics[metric + "_Score"] = (
        driver_metrics[metric]
        .rank(pct=True)
        * 100
    )


# ============================================================
# WEIGHTED DRIVER RISK SCORE
# ============================================================

driver_metrics["Risk_Score"] = (

    0.25 *
    driver_metrics["Speeding_Rate_Score"]

    +

    0.25 *
    driver_metrics["Harsh_Braking_Rate_Score"]

    +

    0.20 *
    driver_metrics["Harsh_Acceleration_Rate_Score"]

    +

    0.15 *
    driver_metrics["Lateral_Event_Rate_Score"]

    +

    0.15 *
    driver_metrics["High_Gyro_Rate_Score"]
)


driver_metrics["Risk_Score"] = (
    driver_metrics["Risk_Score"]
    .round(2)
)


# ============================================================
# RISK CATEGORY
# ============================================================

def classify_risk(score):

    if score <= 30:
        return "Safe"

    elif score <= 60:
        return "Moderate"

    else:
        return "High Risk"


driver_metrics["Risk_Category"] = (
    driver_metrics["Risk_Score"]
    .apply(classify_risk)
)


# ============================================================
# SORT BY RISK
# ============================================================

driver_metrics = driver_metrics.sort_values(
    "Risk_Score",
    ascending=False
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 80)
print("DRIVER BEHAVIOUR ANALYSIS")
print("=" * 80)

display_columns = [
    "Driver_ID",
    "Driver_Name",
    "Total_Telemetry",
    "Speeding_Rate",
    "Harsh_Acceleration_Rate",
    "Harsh_Braking_Rate",
    "Lateral_Event_Rate",
    "High_Gyro_Rate",
    "Risk_Score",
    "Risk_Category"
]

print(
    driver_metrics[display_columns]
    .to_string(index=False)
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("RISK CATEGORY SUMMARY")
print("=" * 80)

print(
    driver_metrics["Risk_Category"]
    .value_counts()
)


# ============================================================
# TOP 5 RISKIEST DRIVERS
# ============================================================

print("\n" + "=" * 80)
print("TOP 5 RISKIEST DRIVERS")
print("=" * 80)

print(
    driver_metrics[
        display_columns
    ]
    .head(5)
    .to_string(index=False)
)


# ============================================================
# TOP 5 SAFEST DRIVERS
# ============================================================

print("\n" + "=" * 80)
print("TOP 5 SAFEST DRIVERS")
print("=" * 80)

print(
    driver_metrics[
        display_columns
    ]
    .tail(5)
    .sort_values("Risk_Score")
    .to_string(index=False)
)


# ============================================================
# SAVE RESULTS
# ============================================================

driver_metrics.to_csv(
    "outputs/driver_scores.csv",
    index=False
)

print("\nDriver scores saved to:")
print("outputs/driver_scores.csv")