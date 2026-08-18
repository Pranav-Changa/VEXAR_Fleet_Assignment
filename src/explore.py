import pandas as pd
import numpy as np

# ============================================================
# LOAD MASTER DATA
# ============================================================

master = pd.read_csv("outputs/master_telemetry.csv")

print("=" * 70)
print("EXPLORATORY DATA ANALYSIS")
print("=" * 70)

print("Rows:", len(master))


# ============================================================
# 1. SPEED DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("SPEED DISTRIBUTION")
print("=" * 70)

print(
    master["Speed_kmph"]
    .describe(
        percentiles=[
            0.50,
            0.75,
            0.90,
            0.95,
            0.99
        ]
    )
    .round(2)
)


# ============================================================
# 2. ACCELERATION DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("ACCELERATION DISTRIBUTION")
print("=" * 70)

print(
    master["Accel_X_g"]
    .describe(
        percentiles=[
            0.01,
            0.05,
            0.95,
            0.99
        ]
    )
    .round(3)
)


# ============================================================
# 3. LATERAL ACCELERATION
# ============================================================

print("\n" + "=" * 70)
print("LATERAL ACCELERATION DISTRIBUTION")
print("=" * 70)

print(
    master["Accel_Y_g"]
    .describe(
        percentiles=[
            0.01,
            0.05,
            0.95,
            0.99
        ]
    )
    .round(3)
)


# ============================================================
# 4. Z-AXIS ACCELERATION
# ============================================================

print("\n" + "=" * 70)
print("Z-AXIS ACCELERATION")
print("=" * 70)

print(
    master["Accel_Z_g"]
    .describe(
        percentiles=[
            0.01,
            0.05,
            0.95,
            0.99
        ]
    )
    .round(3)
)


# ============================================================
# 5. GYROSCOPE MAGNITUDE
# ============================================================

master["Gyro_Magnitude"] = np.sqrt(
    master["Gyro_X_dps"] ** 2
    + master["Gyro_Y_dps"] ** 2
    + master["Gyro_Z_dps"] ** 2
)

print("\n" + "=" * 70)
print("GYROSCOPE MAGNITUDE")
print("=" * 70)

print(
    master["Gyro_Magnitude"]
    .describe(
        percentiles=[
            0.50,
            0.75,
            0.90,
            0.95,
            0.99
        ]
    )
    .round(2)
)
# ============================================================
# 6. TEST GYROSCOPE THRESHOLDS
# ============================================================

print("\n" + "=" * 70)
print("GYROSCOPE THRESHOLD TEST")
print("=" * 70)

for threshold in [8, 10, 12, 15, 20, 25, 30]:

    count = (
        master["Gyro_Magnitude"] > threshold
    ).sum()

    rate = count / len(master) * 100

    print(
        f"Gyro Magnitude > {threshold} dps:"
        f" {count} events ({rate:.2f}%)"
    )

# ============================================================
# 6. TEST POSSIBLE SPEED THRESHOLDS
# ============================================================

print("\n" + "=" * 70)
print("SPEED THRESHOLD TEST")
print("=" * 70)

for threshold in [40, 45, 50, 55, 60]:
    count = (master["Speed_kmph"] > threshold).sum()
    rate = count / len(master) * 100

    print(
        f"Speed > {threshold} km/h:"
        f" {count} events ({rate:.2f}%)"
    )


# ============================================================
# 7. TEST ACCELERATION THRESHOLDS
# ============================================================

print("\n" + "=" * 70)
print("HARSH ACCELERATION THRESHOLD TEST")
print("=" * 70)

for threshold in [0.25, 0.30, 0.35, 0.40, 0.45, 0.50]:

    count = (
        master["Accel_X_g"] > threshold
    ).sum()

    rate = count / len(master) * 100

    print(
        f"Accel X > +{threshold:.2f}g:"
        f" {count} events ({rate:.2f}%)"
    )


# ============================================================
# 8. TEST BRAKING THRESHOLDS
# ============================================================

print("\n" + "=" * 70)
print("HARSH BRAKING THRESHOLD TEST")
print("=" * 70)

for threshold in [0.25, 0.30, 0.35, 0.40, 0.45, 0.50]:

    count = (
        master["Accel_X_g"] < -threshold
    ).sum()

    rate = count / len(master) * 100

    print(
        f"Accel X < -{threshold:.2f}g:"
        f" {count} events ({rate:.2f}%)"
    )


# ============================================================
# 9. TEST LATERAL THRESHOLDS
# ============================================================

print("\n" + "=" * 70)
print("LATERAL EVENT THRESHOLD TEST")
print("=" * 70)

for threshold in [0.15, 0.20, 0.25, 0.30, 0.35]:

    count = (
        master["Accel_Y_g"].abs() > threshold
    ).sum()

    rate = count / len(master) * 100

    print(
        f"|Accel Y| > {threshold:.2f}g:"
        f" {count} events ({rate:.2f}%)"
    )


# ============================================================
# 10. VEHICLE VIBRATION
# ============================================================

master["Z_Deviation"] = (
    master["Accel_Z_g"] - 1.0
).abs()

print("\n" + "=" * 70)
print("Z-AXIS VIBRATION / DEVIATION")
print("=" * 70)

print(
    master["Z_Deviation"]
    .describe(
        percentiles=[
            0.50,
            0.75,
            0.90,
            0.95,
            0.99
        ]
    )
    .round(3)
)


# ============================================================
# 11. TEST VIBRATION THRESHOLDS
# ============================================================

print("\n" + "=" * 70)
print("VIBRATION THRESHOLD TEST")
print("=" * 70)

for threshold in [0.05, 0.10, 0.15, 0.20, 0.25]:

    count = (
        master["Z_Deviation"] > threshold
    ).sum()

    rate = count / len(master) * 100

    print(
        f"|Accel Z - 1g| > {threshold:.2f}g:"
        f" {count} events ({rate:.2f}%)"
    )


# ============================================================
# 12. VEHICLE AGE
# ============================================================

master["Vehicle_Age_Years"] = (
    2026 - master["Manufacture_Year"]
)

print("\n" + "=" * 70)
print("VEHICLE AGE")
print("=" * 70)

print(
    master[
        ["Vehicle_ID", "Manufacture_Year", "Vehicle_Age_Years"]
    ]
    .drop_duplicates()
    .sort_values("Vehicle_Age_Years", ascending=False)
    .to_string(index=False)
)

print("=" * 70)
print("SENSOR PLAUSIBILITY CHECK")
print("=" * 70)

plausibility_checks = {
    "Speed > 80 km/h": (
        master["Speed_kmph"] > 80
    ).sum(),

    "Speed < 0 km/h": (
        master["Speed_kmph"] < 0
    ).sum(),

    "Abs Accel X > 1g": (
        master["Accel_X_g"].abs() > 1
    ).sum(),

    "Abs Accel Y > 1g": (
        master["Accel_Y_g"].abs() > 1
    ).sum(),

    "Accel Z < 0g": (
        master["Accel_Z_g"] < 0
    ).sum(),

    "Gyro Magnitude > 60 dps": (
        master["Gyro_Magnitude"] > 60
    ).sum()
}

for check, count in plausibility_checks.items():
    print(f"{check:<30}: {count}")

print("\n" + "=" * 70)
print("EXPLORATION COMPLETE")
print("=" * 70)