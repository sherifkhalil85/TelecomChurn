import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Telecom Churn Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

### Load Data
@st.cache_data
def load_raw_data():
    """Load the raw telecom customer churn data"""
    try:
        df = pd.read_csv('telecom_customer_churn_clustered.csv')
        return df
    except FileNotFoundError:
        st.error("Raw data file not found. Please ensure Data is available.")
        return None

df = load_raw_data()

##########################################
# Configure sidebar 
sidebar_style = """
    <style>
    [data-testid="stSidebar"] {
        background-color: #f5f5f5;
        padding: 20px;
        border-right: 2px solid #ddd;
    }
    [data-testid="stSidebar"] div {
        font-size: 18px;
        color: #007BFF;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .selected-item {
        background-color: #0056b3;
        color: white;
        padding: 10px;
        font-size: 18px;
        font-weight: bold;
    }
    [data-testid="stSidebar"] div:hover {
        color: #0056b3;
        cursor: pointer;
    }
    </style>
"""
st.markdown(sidebar_style, unsafe_allow_html=True)

# Sidebar content (kept as is)
st.sidebar.title("Navigation")
st.sidebar.write("Select pages above or any options below from the list:")
st.sidebar.markdown("[Data Source](https://www.kaggle.com/datasets/origamik/united-airlines-call-center-sentiment-dataset)")
st.sidebar.markdown("[GitHub Repo](https://github.com/sherifkhalil85/Airline_CC/tree/main)")
st.sidebar.markdown("[Contact Me](https://www.linkedin.com/in/sherif-khalil-62b44823)")

####################################
# Title (kept as is)
st.markdown("""
    <style>
        .title {
            background-color: #ffffff;
            color: #616f89;
            padding: 10px;
            text-align: center;
            font-size: 40px;
            font-weight: bold;
            border: 4px solid #000083;
            border-radius: 10px;
            box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.2);
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            margin-bottom: 20px;
        }
        .metric-card {
            background-color: #ffffff;
            border: 2px solid #000083;
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin-bottom: 15px;
            transition: transform 0.2s ease-in-out;
        }
        .metric-card:hover {
            box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.3);
            transform: scale(1.02);
        }
        .metric-value {
            color: #000083;
            font-size: 26px;
            font-weight: 600;
            font-style: italic;
            text-shadow: 1px 1px 2px #000083;
            margin: 10px 0;
        }
        .metric-label {
            margin-bottom: 5px;
            font-size: 20px;
            font-weight: 500;
            color: #999999;
        }
        .expander-header {
            font-size: 24px !important;
            font-weight: bold !important;
            color: #000083 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">Telecom Churn Analysis Overview</div>', unsafe_allow_html=True)

################################################
# Metrics Calculations

if df is not None:
    # ========== Base Metrics ==========
    customer_base = len(df)
    churned_customers = df[df['Churn'] == 1]['Churn'].sum()  # Your original churn calculation

    # ========== Financial Metrics ==========
    total_revenue = df['Total Revenue'].sum()
    avg_revenue = df['Total Revenue'].mean()
    avg_monthly_charge = df['Average_Monthly_Charge'].mean()
    top_payment = df['Payment Method'].mode()[0]

    # ========== Customer Behavior ==========
    churn_rate = (churned_customers / customer_base) * 100
    avg_tenure = df['Tenure in Months'].mean()
    top_contract = df['Contract'].mode()[0]
    paperless_rate = (df['Paperless Billing'].eq('Yes').sum() / customer_base) * 100

    # ========== Product Adoption ==========
    phone_adoption = (df['Phone Service'].eq('Yes').sum() / customer_base) * 100
    internet_users = (df['Internet Service'].eq('Yes').sum() / customer_base) * 100
    bundle_users = ((df['Phone Service'].eq('Yes') & df['Internet Service'].eq('Yes')).sum() / customer_base) * 100
    top_persona = df['Persona'].mode()[0]

    # ========== Geographic & Demographic ==========
    top_state = df['State'].mode()[0]
    top_city = df['City'].mode()[0]
    top_demo = df['Married_Gender'].mode()[0]

    ###############################################
    # Dashboard Layout

    # Customer Base Metric
    image1= 'https://media.istockphoto.com/id/2155004323/photo/young-african-american-woman-in-colorful-clothing-using-a-smartphone-low-angle-shot-with.jpg?s=2048x2048&w=is&k=20&c=SsSlrrDEkw79nBOW6B7oHsUCN7Q1T8_tv5dkWLZAi4M='
    image2= 'https://media.istockphoto.com/id/1219430151/photo/macro-shot-with-augmented-reality-it-administrator-plugs-in-rj45-internet-connector-into-lan.jpg?s=2048x2048&w=is&k=20&c=mJiozxfieXj3_nY0qlDqPiG7UFxFCJ7HUjHXL51XVcE='
    col1, col2, col3 = st.columns(3)

    image_height = 200  # consistent height for alignment

    with col1:
        st.image(image1, use_container_width =True, output_format='auto')

    with col2:
        st.markdown(f"""
            <div style="height: {image_height}px; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 1px solid #ddd; border-radius: 12px; padding: 10px; background-color: #f9f9f9;">
                <div style="font-size: 16px; font-weight: bold; color: #555;">Total Customer Base</div>
                <div style="font-size: 28px; font-weight: bold; color: #2a9d8f;">{customer_base:,}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.image(image2, use_container_width =True, output_format='auto')


    # Main Metrics in Expanders
    with st.expander("💰 Financial Performance", expanded=False):
        cols = st.columns(2)

        with cols[0]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Revenue</div>
                    <div class="metric-value">${total_revenue:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Avg Revenue per User ARPU</div>
                    <div class="metric-value">${avg_revenue:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

        with cols[1]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Avg Monthly Charge</div>
                    <div class="metric-value">${avg_monthly_charge:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Top Payment Method</div>
                    <div class="metric-value">{top_payment}</div>
                </div>
            """, unsafe_allow_html=True)

    with st.expander("👥 Customer Behavior", expanded=False):
        cols = st.columns(2)

        with cols[0]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Churn Rate</div>
                    <div class="metric-value">{churn_rate:.1f}%</div>
                    <div>({churned_customers:,} customers)</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Avg Customer Tenure</div>
                    <div class="metric-value">{avg_tenure:.1f} months</div>
                </div>
            """, unsafe_allow_html=True)

        with cols[1]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Most Common Contract</div>
                    <div class="metric-value">{top_contract}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Paperless Billing</div>
                    <div class="metric-value">{paperless_rate:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

    with st.expander("📱 Product Adoption", expanded=False):
        cols = st.columns(2)

        with cols[0]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Phone Service</div>
                    <div class="metric-value">{phone_adoption:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Internet Service</div>
                    <div class="metric-value">{internet_users:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        with cols[1]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Phone + Internet Bundle</div>
                    <div class="metric-value">{bundle_users:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Top Customer Persona</div>
                    <div class="metric-value">{top_persona}</div>
                </div>
            """, unsafe_allow_html=True)

    with st.expander("📍 Geographic & Demographic", expanded=False):
        cols = st.columns(3)

        with cols[0]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Top State</div>
                    <div class="metric-value">{top_state}</div>
                </div>
            """, unsafe_allow_html=True)

        with cols[1]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Top City</div>
                    <div class="metric-value">{top_city}</div>
                </div>
            """, unsafe_allow_html=True)

        with cols[2]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Top Demographic</div>
                    <div class="metric-value">{top_demo}</div>
                </div>
            """, unsafe_allow_html=True)

