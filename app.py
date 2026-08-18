import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIG
# ============================================================
page = st.sidebar.radio(
    "Select Dashboard",
    [
        "Executive Overview",
        "Driver Behaviour",
        "Vehicle Health"
    ]
)

# ============================================================
# LOAD DATA
# ============================================================

try:

    drivers = pd.read_csv(
        "outputs/driver_scores.csv"
    )

    vehicles = pd.read_csv(
        "outputs/vehicle_health.csv"
    )

    master = pd.read_csv(
        "outputs/master_telemetry.csv"
    )

    master["Gyro_Magnitude"] = (
        master["Gyro_X_dps"]**2
        + master["Gyro_Y_dps"]**2
        + master["Gyro_Z_dps"]**2
    ) ** 0.5

except FileNotFoundError:

    st.error(
        """
        Required analysis outputs were not found.

        Please run the analysis pipeline first:

        1. python3 src/analysis.py
        2. python3 src/explore.py
        3. python3 src/driver_analysis.py
        4. python3 src/vehicle_analysis.py
        5. streamlit run app.py
        """
    )

    st.stop()
# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("VEXAR Fleet Analytics")

# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":

    st.title("🏍️ VEXAR Fleet Analytics")
    st.subheader("Fleet Safety & Vehicle Health Overview")

    st.markdown(
        """
        This dashboard analyzes one week of two-wheeler delivery-fleet
        telemetry across **30 drivers, 30 vehicles, 450 trips, and
        12,987 minute-level sensor observations**.

        The analysis has two objectives:

        1. Identify drivers exhibiting relatively higher-risk riding
           behaviour.
        2. Identify vehicles showing unusual sensor signatures that may
           warrant maintenance review.

        The scoring framework combines explainable sensor-based event
        rates with fleet-relative percentile scoring. Because the dataset
        contains no labelled accidents, incidents, breakdowns, or
        mechanical failures, the resulting scores are **analytical
        prioritization indicators rather than predictive diagnoses**.
        """
    )

    st.divider()

    # ================================================================
    # FLEET KPIs
    # ================================================================

    total_drivers = master["Driver_ID"].nunique()
    total_vehicles = master["Vehicle_ID"].nunique()
    total_trips = master["Trip_ID"].nunique()
    total_telemetry = len(master)

    high_risk = (
        drivers["Risk_Category"] == "High Risk"
    ).sum()

    maintenance = (
        vehicles["Health_Category"] == "Maintenance Review"
    ).sum()

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Drivers", total_drivers)
    col2.metric("Vehicles", total_vehicles)
    col3.metric("Trips", total_trips)
    col4.metric("Telemetry", f"{total_telemetry:,}")
    col5.metric("High-Risk Drivers", high_risk)
    col6.metric("Maintenance", maintenance)

    st.divider()

    # ================================================================
    # KEY FINDINGS
    # ================================================================

    st.subheader("Key Findings")

    top_driver = drivers.sort_values(
        "Risk_Score",
        ascending=False
    ).iloc[0]

    top_vehicle = vehicles.sort_values(
        "Health_Risk_Score",
        ascending=False
    ).iloc[0]

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### 👤 Driver Behaviour")

        st.markdown(
            f"""
            **{high_risk} of {total_drivers} drivers** are classified
            as High Risk under the current fleet-relative scoring method.

            **Highest observed behavioural-risk driver**

            - Driver: **{top_driver['Driver_ID']} — {top_driver['Driver_Name']}**
            - Risk Score: **{top_driver['Risk_Score']:.2f}/100**
            - Category: **{top_driver['Risk_Category']}**

            The score is based on speeding, harsh acceleration,
            harsh braking, lateral movement, and gyroscope activity.
            """
        )

    with col2:

        st.markdown("### 🛵 Vehicle Health")

        st.markdown(
            f"""
            **{maintenance} of {total_vehicles} vehicles** are currently
            classified for Maintenance Review.

            **Highest sensor-based maintenance priority**

            - Vehicle: **{top_vehicle['Vehicle_ID']}**
            - Health Score: **{top_vehicle['Health_Risk_Score']:.2f}/100**
            - Category: **{top_vehicle['Health_Category']}**

            The score is based on vibration anomalies, gyroscope
            anomalies, and Z-axis variability.
            """
        )

    st.divider()

    # ================================================================
    # HOW TO INTERPRET THE SCORES
    # ================================================================

    st.subheader("How to Interpret These Results")

    st.markdown(
        """
        ### Driver Risk

        A higher Driver Risk Score means that the driver's observed
        behaviour is relatively more concerning **within this fleet**.

        It does **not** mean that the driver has a confirmed high
        probability of an accident.

        The score is based on event rates normalized by telemetry volume
        and converted into fleet-relative percentile scores.

        ### Vehicle Health

        A higher Vehicle Health Risk Score means that the vehicle has
        relatively more unusual sensor behaviour compared with other
        vehicles in the fleet.

        A Maintenance Review classification means the vehicle should
        be considered for inspection. It does **not** establish that
        the vehicle has a mechanical failure.

        Vehicle age, odometer reading, and service recency are shown
        as supporting maintenance context rather than direct evidence
        of mechanical failure.
        """
    )

    st.warning(
        "Important: Driver Risk and Vehicle Health scores are "
        "heuristic, fleet-relative prioritization indicators. "
        "They are not accident predictions, legal safety classifications, "
        "or mechanical-failure diagnoses."
    )

    st.divider()

    # ================================================================
    # KEY METHODOLOGY
    # ================================================================

    st.subheader("Scoring Methodology at a Glance")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            **Driver Risk Score**

            - Speeding → 25%
            - Harsh braking → 25%
            - Harsh acceleration → 20%
            - Lateral movement → 15%
            - Gyroscope activity → 15%

            Event rates are calculated relative to each driver's
            telemetry volume and converted into fleet-relative
            percentile scores.
            """
        )

    with col2:

        st.markdown(
            """
            **Vehicle Health Risk Score**

            - Vibration anomaly → 45%
            - Gyroscope anomaly → 30%
            - Z-axis variability → 25%

            Component scores are based on fleet-relative percentile
            ranking and are intended to prioritize vehicles for
            maintenance inspection.
            """
        )

    st.divider()

    # ================================================================
    # POTENTIAL FUTURE APPLICATIONS
    # ================================================================

    st.subheader("Potential Future Applications")

    st.markdown(
        """
        The same telemetry and fleet data could support:

        - **Predictive maintenance** using historical breakdown records
        - **Driver safety coaching** based on recurring behaviour patterns
        - **Route-level risk analysis** using GPS and event locations
        - **Accident / incident detection** using extreme sensor combinations
        - **Trip-time prediction** using speed, distance and route features
        - **Fleet utilization optimization** using vehicle and trip demand
        - **Sensor anomaly detection** for calibration or hardware issues
        - **Driver performance benchmarking** over longer time periods
        - **Maintenance scheduling** by combining sensor anomalies with
          service history
        """
    )
# ============================================================
# DRIVER DASHBOARD
# ============================================================

if page == "Driver Behaviour":

    st.title("🏍️ Driver Behaviour Dashboard")

    st.markdown(
        """
        ### Fleet driving-risk overview

        This dashboard identifies drivers with elevated behavioural
        risk based on speeding, harsh acceleration, harsh braking,
        lateral movement and rotational activity.
        """
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    total_drivers = len(drivers)

    high_risk = (
        drivers["Risk_Category"]
        == "High Risk"
    ).sum()

    moderate = (
        drivers["Risk_Category"]
        == "Moderate"
    ).sum()

    safe = (
        drivers["Risk_Category"]
        == "Safe"
    ).sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Drivers",
        total_drivers
    )

    col2.metric(
        "High Risk",
        high_risk
    )

    col3.metric(
        "Moderate",
        moderate
    )

    col4.metric(
        "Safe",
        safe
    )

    st.divider()

    # --------------------------------------------------------
    # DRIVER RISK RANKING
    # --------------------------------------------------------

    st.subheader(
        "Driver Risk Ranking"
    )

    ranking = drivers.sort_values(
        "Risk_Score",
        ascending=False
    )

    fig = px.bar(
        ranking,
        x="Driver_ID",
        y="Risk_Score",
        color="Risk_Category",
        hover_data=[
            "Driver_Name",
            "Speeding_Rate",
            "Harsh_Acceleration_Rate",
            "Harsh_Braking_Rate",
            "Lateral_Event_Rate",
            "High_Gyro_Rate"
        ],
        title="Risk Score by Driver"
    )

    fig.update_layout(
        xaxis_title="Driver",
        yaxis_title="Risk Score",
        yaxis_range=[0, 100]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # DRIVER SELECTION
    # --------------------------------------------------------

    st.subheader(
        "Individual Driver Analysis"
    )

    selected_driver = st.selectbox(
        "Select Driver",
        drivers["Driver_ID"].tolist()
    )

    driver = drivers[
        drivers["Driver_ID"]
        == selected_driver
    ].iloc[0]

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Driver",
            driver["Driver_Name"]
        )

        st.metric(
            "Risk Score",
            f"{driver['Risk_Score']:.2f}"
        )

        st.metric(
            "Risk Category",
            driver["Risk_Category"]
        )

    with col2:

        behaviour_data = pd.DataFrame({
            "Behaviour": [
                "Speeding",
                "Harsh Acceleration",
                "Harsh Braking",
                "Lateral Movement",
                "High Gyro"
            ],
            "Rate": [
                driver["Speeding_Rate"],
                driver["Harsh_Acceleration_Rate"],
                driver["Harsh_Braking_Rate"],
                driver["Lateral_Event_Rate"],
                driver["High_Gyro_Rate"]
            ]
        })

        fig2 = px.bar(
            behaviour_data,
            x="Behaviour",
            y="Rate",
            title="Behaviour Event Rates"
        )

        fig2.update_layout(
            yaxis_title="Event Rate (%)",
            xaxis_title=""
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    # --------------------------------------------------------
    # METHODOLOGY
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Methodology & Assumptions"
    )

    st.markdown(
        """
        **Risk indicators**

        - Speeding: Speed > 50 km/h
        - Harsh acceleration: Accel_X > +0.35g
        - Harsh braking: Accel_X < -0.35g
        - Lateral movement: |Accel_Y| > 0.25g
        - High rotational movement: Gyroscope magnitude > 10 dps

        **Risk score weighting**

        - Speeding: 25%
        - Harsh braking: 25%
        - Harsh acceleration: 20%
        - Lateral movement: 15%
        - Gyroscope activity: 15%

        ### Why these weights?

        The weights are a transparent heuristic rather than statistically
        learned coefficients because this dataset does not contain labelled
        accident or incident outcomes.

        Speeding and harsh braking receive the highest weights because
        they are treated as the most direct high-risk longitudinal driving
        behaviours available in the telemetry.

        Harsh acceleration receives a slightly lower weight because it
        represents aggressive longitudinal behaviour but is not necessarily
        unsafe in every context.

        Lateral acceleration and gyroscope activity receive lower weights
        because elevated values can also occur during legitimate cornering,
        turning, road-surface changes, or normal vehicle manoeuvres.

        The weights should therefore be interpreted as an operational
        prioritization heuristic, not as estimated causal contributions
        to accidents.

        Event rates are calculated relative to each driver's telemetry
        volume. Component scores use fleet-relative percentile ranking.

        The score is a heuristic behavioural-risk indicator,
        not an accident prediction.
        """
    )
    st.warning(
    """
    ⚠️ Important interpretation:

    The Driver Risk Score is a fleet-relative prioritization score.
    It compares drivers with other drivers in this dataset; it is
    NOT an absolute measure of legal, regulatory, or accident risk.

    Because percentile ranking is used, the Safe / Moderate /
    High Risk categories are relative to this fleet and should not
    be interpreted as proving that a driver is objectively unsafe.
    """
)

# --------------------------------------------------------
# THRESHOLD JUSTIFICATION
# --------------------------------------------------------
if page == "Driver Behaviour":
    with st.expander("📐 Why were these thresholds selected?"):

        st.markdown(
            """
            The thresholds below are analytical thresholds derived
            from the observed distribution of this fleet's telemetry.

            They are not manufacturer specifications or regulatory
            limits. They are used to identify relatively unusual
            observations within this dataset.
            """
        )
        speed_rate = (
            (master["Speed_kmph"] > 50).mean() * 100
        )

        accel_rate = (
            (master["Accel_X_g"] > 0.35).mean() * 100
        )

        brake_rate = (
            (master["Accel_X_g"] < -0.35).mean() * 100
        )

        lateral_rate = (
            (master["Accel_Y_g"].abs() > 0.25).mean() * 100
        )

        gyro_rate = (
            (master["Gyro_Magnitude"] > 10).mean() * 100
        )

        threshold_data = pd.DataFrame({
            "Metric": [
                "Speeding",
                "Harsh Acceleration",
                "Harsh Braking",
                "Lateral Movement",
                "High Gyroscope Activity"
            ],

            "Threshold": [
                "> 50 km/h",
                "> +0.35g",
                "< -0.35g",
                "|Accel_Y| > 0.25g",
                "Gyro Magnitude > 10 dps"
            ],

            "Fleet Event Rate": [
            f"{speed_rate:.2f}%",
            f"{accel_rate:.2f}%",
            f"{brake_rate:.2f}%",
            f"{lateral_rate:.2f}%",
            f"{gyro_rate:.2f}%"
            ],

            "Reasoning": [
                "Approximately at the upper tail of the fleet speed distribution; the 99th percentile is 51.3 km/h.",
                "Selected to isolate relatively strong positive longitudinal acceleration while retaining enough observations for driver comparison.",
                "Selected to isolate relatively strong negative longitudinal acceleration while retaining enough observations for driver comparison.",
                "Selected to identify relatively strong lateral acceleration events without using the more extreme tail.",
                "Selected to identify elevated rotational movement while retaining sufficient observations for fleet-level comparison."
            ]
        })

        st.dataframe(
            threshold_data,
            use_container_width=True,
            hide_index=True
        )

        st.markdown(
            """
            ### How the final Risk Score is calculated

            For each driver:

            **Step 1 — Event rate**

            Event Rate = Event Count / Driver Telemetry Count × 100

            **Step 2 — Fleet-relative score**

            Each driver's event rate is converted to a percentile
            score relative to the other 30 drivers.

            **Step 3 — Weighted combination**

            The component scores are combined using:

            - Speeding → 25%
            - Harsh braking → 25%
            - Harsh acceleration → 20%
            - Lateral movement → 15%
            - Gyroscope activity → 15%

            Therefore, a driver receives a higher Risk Score when their
            frequency of unusual behaviours is consistently higher
            than other drivers in the fleet.

            **Interpretation:** The score is a behavioural-risk
            prioritization indicator, not an accident prediction.
            """
        )

# ============================================================
# VEHICLE HEALTH DASHBOARD
# ============================================================

if page == "Vehicle Health":

    st.title("🔧 Vehicle Health Status Dashboard")

    st.markdown(
        """
        ### Fleet maintenance-risk overview

        This dashboard identifies vehicles showing unusual
        sensor signatures that may warrant maintenance inspection.
        """
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    total_vehicles = len(vehicles)

    maintenance = (
        vehicles["Health_Category"]
        == "Maintenance Review"
    ).sum()

    monitor = (
        vehicles["Health_Category"]
        == "Monitor"
    ).sum()

    healthy = (
        vehicles["Health_Category"]
        == "Healthy"
    ).sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Vehicles",
        total_vehicles
    )

    col2.metric(
        "Maintenance Review",
        maintenance
    )

    col3.metric(
        "Monitor",
        monitor
    )

    col4.metric(
        "Healthy",
        healthy
    )

    st.divider()

    # --------------------------------------------------------
    # VEHICLE HEALTH RANKING
    # --------------------------------------------------------

    st.subheader(
        "Vehicle Health Risk Ranking"
    )

    ranking = vehicles.sort_values(
        "Health_Risk_Score",
        ascending=False
    )

    fig = px.bar(
        ranking,
        x="Vehicle_ID",
        y="Health_Risk_Score",
        color="Health_Category",
        hover_data=[
            "Make",
            "Model",
            "Vibration_Anomaly_Rate",
            "Gyro_Anomaly_Rate",
            "Vehicle_Age_Years",
            "Days_Since_Last_Service",
            "Odometer_KM"
        ],
        title="Vehicle Health Risk Score"
    )

    fig.update_layout(
        xaxis_title="Vehicle",
        yaxis_title="Health Risk Score",
        yaxis_range=[0, 100]
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # --------------------------------------------------------
    # VEHICLE SELECTION
    # --------------------------------------------------------

    st.subheader(
        "Individual Vehicle Analysis"
    )

    selected_vehicle = st.selectbox(
        "Select Vehicle",
        vehicles["Vehicle_ID"].tolist()
    )

    vehicle = vehicles[
        vehicles["Vehicle_ID"]
        == selected_vehicle
    ].iloc[0]

    # --------------------------------------------------------
    # VEHICLE INFORMATION
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Vehicle",
        vehicle["Vehicle_ID"]
    )

    col2.metric(
        "Health Risk Score",
        f"{vehicle['Health_Risk_Score']:.2f}"
    )

    col3.metric(
    "Status",
    "Maintenance" if vehicle["Health_Category"] == "Maintenance Review"
    else vehicle["Health_Category"]
    )   

    st.divider()

    # --------------------------------------------------------
    # VEHICLE DETAILS
    # --------------------------------------------------------

    st.subheader("Vehicle Details")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Make",
        vehicle["Make"]
    )

    col2.metric(
        "Model",
        vehicle["Model"]
    )

    col3.metric(
        "Vehicle Age",
        f"{vehicle['Vehicle_Age_Years']:.0f} years"
    )

    col4.metric(
        "Odometer",
        f"{vehicle['Odometer_KM']:,.0f} km"
    )

    # --------------------------------------------------------
    # SENSOR METRICS
    # --------------------------------------------------------

    st.subheader(
        "Sensor Anomaly Indicators"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Vibration Anomaly Rate",
            f"{vehicle['Vibration_Anomaly_Rate']:.2f}%"
        )

        st.metric(
            "Mean Z Deviation",
            f"{vehicle['Mean_Z_Deviation']:.3f} g"
        )

    with col2:

        st.metric(
            "Gyroscope Anomaly Rate",
            f"{vehicle['Gyro_Anomaly_Rate']:.2f}%"
        )

        st.metric(
            "Z Deviation Std",
            f"{vehicle['Z_Deviation_Std']:.3f}"
        )

    # --------------------------------------------------------
    # SERVICE INFORMATION
    # --------------------------------------------------------

    st.subheader(
        "Maintenance Context"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Days Since Last Service",
            f"{vehicle['Days_Since_Last_Service']:.0f} days"
        )

    with col2:

        st.metric(
            "Odometer at Week Start",
            f"{vehicle['Odometer_KM']:,.0f} km"
        )

    # --------------------------------------------------------
    # SENSOR PROFILE CHART
    # --------------------------------------------------------

    sensor_data = pd.DataFrame({
        "Indicator": [
            "Vibration Anomaly",
            "Gyro Anomaly"
        ],
        "Rate": [
            vehicle["Vibration_Anomaly_Rate"],
            vehicle["Gyro_Anomaly_Rate"]
        ]
    })

    fig2 = px.bar(
        sensor_data,
        x="Indicator",
        y="Rate",
        title="Sensor Anomaly Rates"
    )

    fig2.update_layout(
        yaxis_title="Anomaly Rate (%)",
        xaxis_title=""
    )

    st.plotly_chart(
        fig2,
        width="stretch"
    )

    # --------------------------------------------------------
    # METHODOLOGY
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Methodology & Assumptions"
    )

    st.markdown(
        """
        **Vehicle anomaly indicators**

        - Vibration anomaly:
          |Accel_Z − 1g| > 0.15g
        - Gyroscope anomaly:
          Gyroscope magnitude > 10 dps

        **Health Risk Score**

        - Vibration anomaly rate: 45%
        - Gyroscope anomaly rate: 30%
        - Z-axis variability: 25%

        ### Why these weights?

        The vehicle-health weights are heuristic because the dataset
        contains no labelled mechanical failures.

        Vibration anomaly receives the highest weight because repeated
        abnormal vertical acceleration is a useful sensor-based indicator
        of irregular ride behaviour in this dataset.

        Gyroscope anomaly receives a secondary weight because unusual
        rotational behaviour may indicate irregular vehicle dynamics,
        although it can also arise from normal manoeuvres.

        Z-axis variability receives the remaining weight because it captures
        consistency of vertical sensor behaviour.

        These weights are intended for maintenance prioritization and should
        be recalibrated when actual maintenance or breakdown labels become
        available.
        
        Component scores are based on fleet-relative
        percentile ranking.

        The resulting score is a maintenance-prioritization
        indicator, not a diagnosis of mechanical failure.

        ### Maintenance context vs. sensor evidence

        Vehicle age, odometer and service recency are intentionally
        excluded from the Health Risk Score. The score is designed to
        represent sensor-based anomaly evidence rather than combine
        live telemetry with static maintenance information.

        These fields are therefore shown as supporting maintenance
        context. A vehicle with a high sensor-risk score that is also
        older, high-mileage, or overdue for service may warrant higher
        inspection priority.

        Age or mileage alone does not establish mechanical deterioration,
        so these variables are not treated as direct evidence of failure.

        ### Sensor feature limitation

        Vibration anomaly rate and Z-axis variability are both
        derived from the vertical acceleration signal. They therefore
        represent related rather than completely independent evidence.

        The current weighting is a transparent heuristic for fleet
        prioritization and should be reassessed using historical
        maintenance or breakdown outcomes when available.
        """
    )
    st.warning(
    """
    ⚠️ Important interpretation:

    The Vehicle Health Risk Score is a fleet-relative sensor-anomaly
    prioritization score.

    "Maintenance Review" means the vehicle shows relatively unusual
    sensor behaviour compared with this fleet; it does NOT establish
    mechanical failure.
    """
)
    # --------------------------------------------------------
    # VEHICLE THRESHOLD JUSTIFICATION
    # --------------------------------------------------------

    with st.expander(
        "🔧 Why were these vehicle-health thresholds selected?"
    ):

        st.markdown(
            """
            The vehicle-health thresholds are analytical anomaly
            thresholds derived from the observed sensor
            distributions.

            They are not manufacturer specifications or regulatory
            limits. They are used to identify relatively unusual
            sensor behaviour within this fleet.
            """
        )
        vibration_context_rate = (
            (abs(master["Accel_Z_g"] - 1) > 0.15).mean() * 100
        )

        gyro_context_rate = (
            (master["Gyro_Magnitude"] > 10).mean() * 100
        )

        vehicle_threshold_data = pd.DataFrame({

            "Indicator": [
                "Vibration Anomaly",
                "Gyroscope Anomaly",
                "Z-axis Variability"
            ],

            "Definition": [
                "|Accel_Z - 1g| > 0.15g",
                "Gyro Magnitude > 10 dps",
                "Standard deviation of Z-axis deviation"
            ],

            "Fleet Context": [
                f"{vibration_context_rate:.2f}% of telemetry observations exceed 0.15g deviation.",
                f"{gyro_context_rate:.2f}% of telemetry observations exceed 10 dps.",
                "Used to compare consistency of vertical sensor behaviour."
            ],

            "Reasoning": [
                "Focuses on relatively uncommon vertical acceleration deviations.",
                "Identifies elevated rotational movement while retaining enough observations for comparison.",
                "Higher variability indicates less consistent vertical sensor behaviour."
            ]
        })

        st.dataframe(
            vehicle_threshold_data,
            use_container_width=True,
            hide_index=True
        )

        st.markdown(
            """
            ### How the Vehicle Health Risk Score is calculated

            **Step 1 — Anomaly rate**

            Anomaly Rate =
            Anomaly Count / Vehicle Telemetry Count × 100

            **Step 2 — Fleet-relative score**

            Each vehicle's anomaly metrics are converted into
            percentile scores relative to the other 30 vehicles.

            **Step 3 — Weighted combination**

            - Vibration anomaly → 45%
            - Gyroscope anomaly → 30%
            - Z-axis variability → 25%

            A higher score means the vehicle exhibits relatively
            unusual sensor behaviour compared with other vehicles.

            Vehicle age, odometer and service recency are shown
            as maintenance context rather than direct evidence
            of mechanical failure.

            **Interpretation:** The score prioritizes vehicles
            for inspection; it does not diagnose a mechanical fault.
            """
        )
    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------

    st.subheader(
        "Recommended Action"
    )

    if vehicle["Health_Category"] == "Maintenance Review":

        st.warning(
            "This vehicle shows elevated sensor anomalies "
            "relative to the fleet. Prioritize it for "
            "physical inspection and maintenance review."
        )

    elif vehicle["Health_Category"] == "Monitor":

        st.info(
            "This vehicle shows moderate sensor anomalies. "
            "Continue monitoring its telemetry and service history."
        )

    else:

        st.success(
            "No major sensor anomaly signal was identified. "
            "Continue routine maintenance and monitoring."
        )