import pandas as pd

# ============================================================
# 1. FILE LOCATION
# ============================================================

file_path = "data/Copy of VEXAR_Fleet_Dataset_CANDIDATE_VERSION.xlsx"


# ============================================================
# 2. LOAD DATA
# ============================================================

drivers = pd.read_excel(
    file_path,
    sheet_name="Drivers",
    header=2
)

vehicles = pd.read_excel(
    file_path,
    sheet_name="Vehicles",
    header=2
)

trips = pd.read_excel(
    file_path,
    sheet_name="Trips",
    header=2
)

telemetry = pd.read_excel(
    file_path,
    sheet_name="Telemetry",
    header=2
)


# ============================================================
# 3. CONVERT DATE/TIME COLUMNS
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
# 4. BASIC DATASET INFORMATION
# ============================================================

print("\n" + "=" * 70)
print("DATASET SUMMARY")
print("=" * 70)

print(f"Drivers    : {len(drivers)}")
print(f"Vehicles   : {len(vehicles)}")
print(f"Trips      : {len(trips)}")
print(f"Telemetry  : {len(telemetry)}")


# ============================================================
# 5. CHECK MISSING VALUES
# ============================================================

print("\n" + "=" * 70)
print("MISSING VALUES")
print("=" * 70)

print("\nDrivers:")
print(drivers.isna().sum())

print("\nVehicles:")
print(vehicles.isna().sum())

print("\nTrips:")
print(trips.isna().sum())

print("\nTelemetry:")
print(telemetry.isna().sum())


# ============================================================
# 6. CHECK DUPLICATES
# ============================================================

print("\n" + "=" * 70)
print("DUPLICATES")
print("=" * 70)

print("Driver duplicates   :", drivers.duplicated().sum())
print("Vehicle duplicates  :", vehicles.duplicated().sum())
print("Trip duplicates     :", trips.duplicated().sum())
print("Telemetry duplicates:", telemetry.duplicated().sum())


# ============================================================
# 7. CHECK UNIQUE IDs
# ============================================================

print("\n" + "=" * 70)
print("UNIQUE IDs")
print("=" * 70)

print("Unique Drivers :", drivers["Driver_ID"].nunique())
print("Unique Vehicles:", vehicles["Vehicle_ID"].nunique())
print("Unique Trips   :", trips["Trip_ID"].nunique())


# ============================================================
# 8. CHECK TABLE RELATIONSHIPS
# ============================================================

print("\n" + "=" * 70)
print("JOIN VALIDATION")
print("=" * 70)

invalid_trip_drivers = ~trips["Driver_ID"].isin(
    drivers["Driver_ID"]
)

invalid_trip_vehicles = ~trips["Vehicle_ID"].isin(
    vehicles["Vehicle_ID"]
)

invalid_telemetry_trips = ~telemetry["Trip_ID"].isin(
    trips["Trip_ID"]
)

print(
    "Trips with invalid Driver_ID:",
    invalid_trip_drivers.sum()
)

print(
    "Trips with invalid Vehicle_ID:",
    invalid_trip_vehicles.sum()
)

print(
    "Telemetry with invalid Trip_ID:",
    invalid_telemetry_trips.sum()
)


# ============================================================
# 9. TRIPS PER DRIVER
# ============================================================

print("\n" + "=" * 70)
print("TRIPS PER DRIVER")
print("=" * 70)

trips_per_driver = trips.groupby("Driver_ID").size()

print(trips_per_driver.describe())

print("\nCounts:")
print(trips_per_driver.value_counts().sort_index())


# ============================================================
# 10. TRIPS PER VEHICLE
# ============================================================

print("\n" + "=" * 70)
print("TRIPS PER VEHICLE")
print("=" * 70)

trips_per_vehicle = trips.groupby("Vehicle_ID").size()

print(trips_per_vehicle.describe())

print("\nCounts:")
print(trips_per_vehicle.value_counts().sort_index())


# ============================================================
# 11. TELEMETRY RECORDS PER TRIP
# ============================================================

print("\n" + "=" * 70)
print("TELEMETRY RECORDS PER TRIP")
print("=" * 70)

telemetry_per_trip = telemetry.groupby("Trip_ID").size()

print(telemetry_per_trip.describe())


# ============================================================
# 12. SENSOR SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("TELEMETRY SENSOR SUMMARY")
print("=" * 70)

sensor_columns = [
    "Speed_kmph",
    "Accel_X_g",
    "Accel_Y_g",
    "Accel_Z_g",
    "Gyro_X_dps",
    "Gyro_Y_dps",
    "Gyro_Z_dps"
]

print(
    telemetry[sensor_columns].describe().round(3)
)


print("\n" + "=" * 70)
print("DATA VALIDATION COMPLETE")
print("=" * 70)