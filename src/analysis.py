import pandas as pd
import numpy as np

# ============================================================
# FILE PATH
# ============================================================

FILE_PATH = "data/Copy of VEXAR_Fleet_Dataset_CANDIDATE_VERSION.xlsx"


# ============================================================
# LOAD DATA
# ============================================================

drivers = pd.read_excel(
    FILE_PATH,
    sheet_name="Drivers",
    header=2
)

vehicles = pd.read_excel(
    FILE_PATH,
    sheet_name="Vehicles",
    header=2
)

trips = pd.read_excel(
    FILE_PATH,
    sheet_name="Trips",
    header=2
)

telemetry = pd.read_excel(
    FILE_PATH,
    sheet_name="Telemetry",
    header=2
)


# ============================================================
# DATE/TIME CONVERSION
# ============================================================

drivers["Date_Joined_Fleet"] = pd.to_datetime(
    drivers["Date_Joined_Fleet"]
)

vehicles["Registration_Date"] = pd.to_datetime(
    vehicles["Registration_Date"]
)

vehicles["Last_Service_Date"] = pd.to_datetime(
    vehicles["Last_Service_Date"]
)

trips["Trip_Date"] = pd.to_datetime(
    trips["Trip_Date"]
)

telemetry["Timestamp"] = pd.to_datetime(
    telemetry["Timestamp"]
)


# ============================================================
# CREATE MASTER TELEMETRY TABLE
# ============================================================

master = telemetry.merge(
    trips[
        [
            "Trip_ID",
            "Driver_ID",
            "Vehicle_ID",
            "Trip_Date",
            "Duration_Min",
            "Distance_KM",
            "Avg_Speed_kmph",
            "Max_Speed_kmph"
        ]
    ],
    on=["Trip_ID", "Driver_ID", "Vehicle_ID"],
    how="left",
    suffixes=("", "_trip")
)


# Add driver information

master = master.merge(
    drivers[
        [
            "Driver_ID",
            "Driver_Name",
            "Age",
            "Gender",
            "License_Experience_Years",
            "Primary_Vehicle_ID",
            "Home_Hub"
        ]
    ],
    on="Driver_ID",
    how="left"
)


# Add vehicle information

master = master.merge(
    vehicles[
        [
            "Vehicle_ID",
            "Vehicle_Type",
            "Make",
            "Model",
            "Manufacture_Year",
            "Registration_Date",
            "Odometer_KM_Start_of_Week",
            "Last_Service_Date"
        ]
    ],
    on="Vehicle_ID",
    how="left"
)


# ============================================================
# CHECK MASTER TABLE
# ============================================================

print("=" * 70)
print("MASTER DATASET")
print("=" * 70)

print("Rows:", len(master))
print("Columns:", len(master.columns))

print("\nColumns:")
print(master.columns.tolist())

print("\nMissing values after joins:")
print(master.isna().sum())

print("\nFirst 5 rows:")
print(master.head())


# ============================================================
# SAVE MASTER DATASET
# ============================================================

master.to_csv(
    "outputs/master_telemetry.csv",
    index=False
)

print("\nMaster dataset saved successfully.")
