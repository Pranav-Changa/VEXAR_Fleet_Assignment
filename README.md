# VEXAR Fleet Analytics

## Data Scientist Intern Assignment

This project analyzes one week of two-wheeler delivery/rider fleet data
from VexarDrive Technologies.

The dataset contains:

- 30 drivers
- 30 vehicles
- 450 trips
- 12,987 minute-level telemetry observations

The project produces two interactive dashboards:

1. Driver Behaviour Dashboard
2. Vehicle Health Status Dashboard

---

## 1. Problem Statement

The objective is to use trip-level and minute-level GPS/IMU telemetry
to identify risky driving behaviour and vehicles showing unusual
sensor patterns that may require maintenance review.

The analysis focuses on explainable, rule-based and fleet-relative
indicators because the dataset does not contain labelled accident,
breakdown, or mechanical-failure outcomes.

---

## 2. Dataset Structure

The input Excel workbook contains four sheets:

### Drivers
Master data containing driver information.

### Vehicles
Master data containing vehicle information.

### Trips
Trip-level information including duration, distance and speed.

### Telemetry
Minute-level GPS, accelerometer and gyroscope readings.

### Dataset relationships


Telemetry.Trip_ID
        ↓
Trips.Trip_ID
        ↓
Trips.Driver_ID → Drivers.Driver_ID
        ↓
Trips.Vehicle_ID → Vehicles.Vehicle_ID

The final joined telemetry dataset contains 12,987 observations.

---

## 3. Data Validation

The validation process checks:

- Missing values
- Duplicate records
- Unique IDs
- Foreign-key integrity
- Trips per driver
- Trips per vehicle
- Telemetry records per trip
- Sensor distributions
- Sensor plausibility

The supplied dataset contains:

- 30 unique drivers
- 30 unique vehicles
- 450 unique trips
- No missing values in the validated columns
- No duplicate records
- No invalid driver/vehicle/trip relationships

A sensor plausibility screening was also performed. No observations
exceeded the predefined sanity-check limits for speed, acceleration,
or gyroscope magnitude.

Extreme observations were retained rather than automatically removed
because they may represent genuine riding events rather than sensor
errors.

---

## 4. Analysis Pipeline

Run the scripts from the project root in the following order:

```bash
python3 src/analysis.py
python3 src/explore.py
python3 src/driver_analysis.py
python3 src/vehicle_analysis.py
streamlit run app.py

### Script responsibilities

`analysis.py`

Creates the master joined telemetry dataset.

`explore.py`

Performs exploratory analysis, threshold testing, sensor distribution
analysis, vehicle-age analysis and sensor plausibility checks.

`driver_analysis.py`

Calculates driver-level behaviour metrics and Driver Risk Scores.

`vehicle_analysis.py`

Calculates vehicle-level anomaly metrics and Vehicle Health Risk Scores.

`app.py`

Runs the Streamlit dashboards.

---

## 5. Driver Behaviour Dashboard

The Driver Behaviour Dashboard evaluates five behaviour indicators:

- Speeding
- Harsh acceleration
- Harsh braking
- Lateral movement
- Gyroscope activity

### Event Rate Calculation

For each driver:

```
Event Rate = (Number of telemetry observations satisfying the event condition
              / Total telemetry observations for that driver) × 100
```

This normalizes the metrics for differences in telemetry volume.

### Behaviour Thresholds

The current analytical thresholds are:

| Indicator | Threshold |
|---|---|
| Speeding | > 50 km/h |
| Harsh acceleration | > +0.35g |
| Harsh braking | < -0.35g |
| Lateral movement | \|Accel_Y\| > 0.25g |
| Gyroscope activity | > 10 dps |

These thresholds are analytical thresholds based on the observed fleet data.

They are **not**:

- Legal speed limits
- Manufacturer specifications
- Regulatory safety thresholds

### Driver Risk Score

The component weights are:

| Component | Weight |
|---|---|
| Speeding | 25% |
| Harsh braking | 25% |
| Harsh acceleration | 20% |
| Lateral movement | 15% |
| Gyroscope activity | 15% |

The weights are transparent heuristics rather than statistically learned coefficients because the dataset does not contain labelled accident or incident outcomes.

Speeding and harsh braking receive the highest weights because they are treated as the most direct high-risk longitudinal driving behaviours available in the telemetry.

Harsh acceleration receives a slightly lower weight because it represents aggressive longitudinal behaviour but is not necessarily unsafe in every context.

Lateral acceleration and gyroscope activity receive lower weights because elevated values can also occur during legitimate cornering, turning, road-surface changes, or normal vehicle manoeuvres.

The weights should therefore be interpreted as an operational prioritization heuristic, not as estimated causal contributions to accidents.

### Score Normalization

Component event rates are converted into fleet-relative percentile scores and combined into a 0–100 Driver Risk Score.

The score is therefore a fleet-relative prioritization indicator, not an absolute measure of legal, regulatory, or accident risk.

Because percentile ranking is used, the Safe / Moderate / High Risk categories are relative to this fleet and should not be interpreted as proof that a driver is objectively unsafe.

## 6. Vehicle Health Dashboard

The Vehicle Health Dashboard identifies vehicles with relatively unusual sensor behaviour that may warrant maintenance review.

### Sensor Indicators

**Vibration Anomaly**

```
|Accel_Z - 1g| > 0.15g
```

**Gyroscope Anomaly**

```
Gyroscope magnitude > 10 dps
```

**Z-axis Variability**

Measures variability in the deviation of vertical acceleration from approximately 1g.

### Health Risk Score

The component weights are:

| Component | Weight |
|---|---|
| Vibration anomaly rate | 45% |
| Gyroscope anomaly rate | 30% |
| Z-axis variability | 25% |

The weights are heuristic because the dataset contains no labelled mechanical failures.

Vibration anomaly receives the highest weight because repeated abnormal vertical acceleration is a useful sensor-based indicator of irregular ride behaviour in this dataset.

Gyroscope anomaly receives a secondary weight because unusual rotational behaviour may indicate irregular vehicle dynamics, although it can also arise from normal manoeuvres.

Z-axis variability receives the remaining weight because it captures consistency of vertical sensor behaviour.

These weights are intended for maintenance prioritization and should be recalibrated when actual maintenance or breakdown labels become available.

### Score Interpretation

Component scores are based on fleet-relative percentile ranking.

The resulting score is a maintenance-prioritization indicator, not a diagnosis of mechanical failure.

A vehicle classified for maintenance review should therefore be treated as a candidate for inspection rather than as a confirmed mechanical failure.

### Maintenance Context vs. Sensor Evidence

Vehicle age, odometer and service recency are intentionally excluded from the Health Risk Score.

The score is designed to represent sensor-based anomaly evidence rather than combine live telemetry with static maintenance information.

These fields are shown as supporting maintenance context.

A vehicle with a high sensor-risk score that is also older, high-mileage, or overdue for service may warrant higher inspection priority.

Age or mileage alone does not establish mechanical deterioration, so these variables are not treated as direct evidence of failure.

### Sensor Feature Limitation

Vibration anomaly rate and Z-axis variability are both derived from the vertical acceleration signal.

They therefore represent related rather than completely independent evidence.

The current weighting is a transparent heuristic for fleet prioritization and should be reassessed using historical maintenance or breakdown outcomes when available.

## 7. Threshold Interpretation

The thresholds in this project are analytical thresholds designed to identify relatively unusual observations within the supplied fleet.

They should not be interpreted as:

- Legal speed limits
- Manufacturer limits
- Regulatory safety standards
- Confirmed mechanical-failure thresholds

For production use, thresholds should be calibrated using operational data, manufacturer specifications, and historical incident or maintenance records.

## 8. Data Volume Limitation

Telemetry counts vary across drivers and vehicles because trip durations are different.

Event rates are normalized by the available telemetry observations, but entities with fewer observations may have less stable event-rate estimates.

The current analysis does not apply statistical shrinkage or confidence intervals.

Low-volume drivers and vehicles should therefore be interpreted with additional caution.

## 9. Additional Applications

The dataset could support several future applications.

**Predictive Maintenance**

Historical maintenance and breakdown records could be combined with sensor anomalies to predict which vehicles are likely to require maintenance.

**Driver Safety Coaching**

Repeated harsh braking, acceleration, lateral movement, or speeding patterns could identify drivers who may benefit from targeted coaching.

**Accident / Incident Detection**

Extreme combinations of speed, acceleration and gyroscope activity could be used to flag potential incidents for investigation.

This would require validation against actual incident records before being used operationally.

**Route Risk Analysis**

GPS coordinates could be aggregated to identify road segments associated with repeated harsh manoeuvres or unusual vehicle behaviour.

**Trip-Time Prediction**

Distance, speed, route and trip-duration data could support ETA and delivery-time prediction.

**Fleet Utilization Optimization**

Trip frequency, distance and vehicle usage could support better vehicle allocation across hubs.

**Sensor Anomaly Detection**

Time-series anomaly detection could identify sensor degradation, calibration issues, or unusual telemetry patterns.

**Driver Performance Benchmarking**

Driver behaviour metrics could be tracked over time to identify improvement or deterioration.

**Maintenance Prioritization**

Sensor anomalies combined with service history could help prioritize vehicle inspections and reduce unnecessary preventive maintenance.

## 10. Limitations

- The dataset does not contain accident or mechanical-failure labels.
- Driver and vehicle scores are heuristic rather than learned from labelled outcomes.
- Percentile scoring is relative to the supplied fleet.
- Telemetry volume varies across entities.
- Low-volume entities may have less stable event-rate estimates.
- Some sensor features are correlated.
- The Z-axis anomaly measures are related and should not be considered completely independent.
- The thresholds should be recalibrated before production deployment.
- The current system should not be interpreted as an accident predictor or mechanical-failure diagnosis.
- The current scoring methodology has not been validated against real-world accident or maintenance outcomes.

## 11. Future Improvements

If labelled accident and maintenance outcomes become available, the system could be extended with supervised predictive models and evaluated using proper train/test validation.

Historical maintenance records could also be used to calibrate vehicle health thresholds and determine whether sensor anomalies predict actual mechanical problems.

Feature correlation and sensitivity analysis could be performed to evaluate whether individual indicators or weights disproportionately influence the final scores.

Confidence intervals or statistical shrinkage could also be introduced to account for differences in telemetry volume between drivers and vehicles.

## 12. Technologies

- Python
- Pandas
- NumPy
- OpenPyXL
- Plotly
- Streamlit

## 13. Project Structure

```
VEXAR_Fleet_Assignment/
│
├── data/
│   └── VEXAR Fleet Dataset.xlsx
│
├── outputs/
│   ├── master_telemetry.csv
│   ├── driver_scores.csv
│   └── vehicle_health.csv
│
├── src/
│   ├── analysis.py
│   ├── explore.py
│   ├── driver_analysis.py
│   └── vehicle_analysis.py
│
├── app.py
├── test_data.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 14. Quick Start

From the project root:

```bash
python3 test_data.py

python3 src/analysis.py

python3 src/explore.py

python3 src/driver_analysis.py

python3 src/vehicle_analysis.py

streamlit run app.py
```

The Streamlit application provides:

- Executive Overview 
- Driver Behaviour Dashboard
- Vehicle Health Status Dashboard

