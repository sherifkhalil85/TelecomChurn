
import streamlit as st
import pandas as pd
import joblib
import numpy as np

# ----------------------------
# Load pipelines
# ----------------------------
@st.cache_resource
def load_classification_pipeline():
    return joblib.load("pipeline.pkl")

@st.cache_resource
def load_clustering_pipeline():
    return joblib.load("clustering_pipeline.pkl")

# Load both models
pipeline = load_classification_pipeline()
clustering_pipeline = load_clustering_pipeline()

# ----------------------------
# Load retention strategies
# ----------------------------
@st.cache_data
def load_retention_data():
    retention_data = {
        'Cluster': [0, 1, 2, 3, 4],
        'Persona': [
            "C - Data-Capped Digitals",
            "A - Premium Loyal Customers",
            "E - Churn-Risk New Users",
            "B - Balanced Bundle Seekers",
            "D - Legacy Phone-Only Users"
        ],
        'Retention_Strategy': [
            "Upsell unlimited data plans and streaming bundles",
            "Offer VIP loyalty rewards and early upgrades",
            "Provide contract incentives and personalized offers",
            "Create customized streaming/data bundles",
            "Introduce internet bundles with education"
        ]
    }
    return pd.DataFrame(retention_data)

retention_df = load_retention_data()
cluster_mapping = retention_df.set_index('Cluster')['Persona'].to_dict()
#----------load City -----------------

@st.cache_data
def load_unique_cities():
    # Replace with your actual data loading method
    # Example: pd.read_csv('data.csv')['City'].unique()
    return np.sort(pd.read_csv('telecom_customer_churn_clustered.csv', usecols=['City'])['City'].dropna().unique())

# 2. In your form section, replace the city input with:
cities = load_unique_cities()

# ----------------------------
# Streamlit App
# ----------------------------
st.title("📊 Telecom Customer Churn & Segmentation")

# Binary mapping
y_n_mapping = {"Yes": 1, "No": 0, "No internet service": 0, "No phone service": 0}

# ----------------------------
# Input Form
# ----------------------------
with st.form("customer_form"):
    # Personal Info
    st.subheader("Personal Information")
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("Gender", ["Male", "Female"])
        age = st.number_input("Age", min_value=0, value=35)
        married = st.selectbox("Married", ["Yes", "No"])
    with col2:
        referrals = st.number_input("Number of Referrals", min_value=0, value=0)
        dependents = st.number_input("Number of Dependents", min_value=0, value=0)

    # Services
    st.subheader("Service Information")
    phone_service = st.selectbox("Phone Service", ["Yes", "No"])
    multiple_lines = st.selectbox("Multiple Lines", ["Yes", "No", "No phone service"])
    internet_type = st.selectbox("Internet Type", ["DSL", "Fiber Optic", "Cable", "no_internet_service"])
    contract = st.selectbox("Contract", ["Month-to-Month", "One Year", "Two Year"])
    payment_method = st.selectbox("Payment Method", ["Bank Withdrawal", "Credit Card", "Mailed Check"])
    paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
    offer = st.selectbox("Offer", ["Offer A", "Offer B", "Offer C", "Offer D", "Offer E", "No_Offer"])
    city =  st.selectbox("City", options=["Unknown"] + cities.tolist(),index=0  )

    # Usage
    st.subheader("Usage Metrics")
    col1, col2 = st.columns(2)
    with col1:
        tenure = st.number_input("Tenure in Months", min_value=1, value=12)
        avg_long_distance = st.number_input("Avg Monthly Long Distance Charges", min_value=0.0, value=15.0)
        avg_monthly_gb = st.number_input("Avg Monthly GB Download", min_value=0.0, value=50.0)
    with col2:
        current_charge = st.number_input("Current Monthly Charge", min_value=0.0, value=75.0)
        total_charges = st.number_input("Total Charges", min_value=0.0, value=1000.0)
        total_refunds = st.number_input("Total Refunds", min_value=0.0, value=0.0)
        total_revenue = total_charges - total_refunds
        extra_data_charges = st.number_input("Total Extra Data Charges", min_value=0.0, value=0.0)
        total_long_distance = st.number_input("Total Long Distance Charges", min_value=0.0, value=500.0)

    # Extra services
    with st.expander("Advanced Service Features"):
        online_security = st.selectbox("Online Security", ["Yes", "No", "No internet service"])
        online_backup = st.selectbox("Online Backup", ["Yes", "No", "No internet service"])
        device_protection = st.selectbox("Device Protection", ["Yes", "No", "No internet service"])
        tech_support = st.selectbox("Tech Support", ["Yes", "No", "No internet service"])
        streaming_tv = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"])
        streaming_movies = st.selectbox("Streaming Movies", ["Yes", "No", "No internet service"])
        streaming_music = st.selectbox("Streaming Music", ["Yes", "No", "No internet service"])
        unlimited_data = st.selectbox("Unlimited Data", ["Yes", "No"])

    submitted = st.form_submit_button("Predict Churn & Segment")

if submitted:
    try:
        avg_monthly_charge = total_charges / tenure if tenure > 0 else 0
        sub_services_count = sum([
            y_n_mapping[online_security], y_n_mapping[online_backup],
            y_n_mapping[device_protection], y_n_mapping[tech_support],
            y_n_mapping[streaming_tv], y_n_mapping[streaming_movies],
            y_n_mapping[streaming_music], y_n_mapping[unlimited_data]
        ])

        input_data = {
            'Gender': gender,
            'Age': age,
            'Married': y_n_mapping[married],
            'Number of Dependents': dependents,
            'City': city,
            'Number of Referrals': referrals,
            'Tenure in Months': tenure,
            'Offer': offer,
            'Phone Service': y_n_mapping[phone_service],
            'Avg Monthly Long Distance Charges': avg_long_distance,
            'Multiple Lines': y_n_mapping[multiple_lines],
            'Internet Service': 1 if internet_type != "no_internet_service" else 0,
            'Internet Type': internet_type,
            'Avg Monthly GB Download': avg_monthly_gb,
            'Online Security': y_n_mapping[online_security],
            'Online Backup': y_n_mapping[online_backup],
            'Device Protection Plan': y_n_mapping[device_protection],
            'Premium Tech Support': y_n_mapping[tech_support],
            'Streaming TV': y_n_mapping[streaming_tv],
            'Streaming Movies': y_n_mapping[streaming_movies],
            'Streaming Music': y_n_mapping[streaming_music],
            'Unlimited Data': y_n_mapping[unlimited_data],
            'Contract': contract,
            'Paperless Billing': y_n_mapping[paperless_billing],
            'Payment Method': payment_method,
            'Current Monthly Charge': current_charge,
            'Total Charges': total_charges,
            'Total Refunds': total_refunds,
            'Total Extra Data Charges': extra_data_charges,
            'Total Long Distance Charges': total_long_distance,
            'Total Revenue': total_revenue,
            'Average_Monthly_Charge': avg_monthly_charge,
            'Sub_Services': sub_services_count
        }

        input_df = pd.DataFrame([input_data])
        prediction = pipeline.predict(input_df)[0]
        proba = pipeline.predict_proba(input_df)[0][1]

        # ---- Raw input for clustering (non-mapped) ----
        cluster_input_data = {
            'Gender': gender,
            'Age': age,
            'Married': married,
            'Number of Dependents': dependents,
            'City': city,
            'Number of Referrals': referrals,
            'Tenure in Months': tenure,
            'Offer': offer,
            'Phone Service': phone_service,
            'Avg Monthly Long Distance Charges': avg_long_distance,
            'Multiple Lines': multiple_lines,
            'Internet Service': "Yes" if internet_type != "no_internet_service" else "No",
            'Internet Type': internet_type,
            'Avg Monthly GB Download': avg_monthly_gb,
            'Online Security': online_security,
            'Online Backup': online_backup,
            'Device Protection Plan': device_protection,
            'Premium Tech Support': tech_support,
            'Streaming TV': streaming_tv,
            'Streaming Movies': streaming_movies,
            'Streaming Music': streaming_music,
            'Unlimited Data': unlimited_data,
            'Contract': contract,
            'Paperless Billing': paperless_billing,
            'Payment Method': payment_method,
            'Current Monthly Charge': current_charge,
            'Total Charges': total_charges,
            'Total Refunds': total_refunds,
            'Total Extra Data Charges': extra_data_charges,
            'Total Long Distance Charges': total_long_distance,
            'Total Revenue': total_revenue,
            'Average_Monthly_Charge': avg_monthly_charge,
            'Sub_Services': sub_services_count
        }
        #total_revenue = total_charges - total_refunds
        cluster_input_df = pd.DataFrame([cluster_input_data])
        cluster_input_df = cluster_input_df[clustering_pipeline.feature_names_in_]
        cluster = clustering_pipeline.predict(cluster_input_df)[0]
        persona = cluster_mapping.get(cluster, "Unknown")
        strategy = retention_df.loc[retention_df['Cluster'] == cluster, 'Retention_Strategy'].values[0]

        # Display
        st.subheader("📊 Prediction Results")
        st.metric("Churn Prediction", "🔴 Churn" if prediction == 1 else "🔵 No Churn", delta=f"{proba:.2%}")

        st.metric("Customer Segment", f"{cluster} - {persona}")

        if proba >0.15:
            st.info(f"**Retention Strategy:** {strategy}")
        else:
            st.info("✅ No need for proactive retention offers")


    except Exception as e:
        st.error(f"Error: {str(e)}")
