
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import streamlit as st

churn_color = {'Joined':'#2ca02c', 'Stayed':'#1f77b4', 'Churned':'#ff7f0e'}

# Page configuration
st.set_page_config(
    page_title="Analysis Dashboard",
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
# Main Dashboard

st.title("Demographic Analysis Dashboard")
st.markdown("""
This dashboard provides insights into customer demographics and their relationship with churn.
""")

# Create expandable filter section
with st.expander("🔍 FILTERS", expanded=False):
    # Create columns for filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Age range filter
        min_age, max_age = st.slider(
            "Select Age Range",
            min_value=int(df['Age'].min()),
            max_value=int(df['Age'].max()),
            value=(int(df['Age'].min()), int(df['Age'].max()))
        )

    with col2:
        # Gender filter
        gender_filter = st.multiselect(
            "Select Gender(s)",
            options=df['Gender'].unique(),
            default=df['Gender'].unique()
        )

    with col3:
        # Persona filter
        persona_filter = st.multiselect(
            "Select Persona(s)",
            options=df['Persona'].unique() if 'Persona' in df.columns else [],
            default=df['Persona'].unique() if 'Persona' in df.columns else []
        )

    with col4:
        # Customer status filter
        status_filter = st.multiselect(
            "Select Customer Status",
            options=df['Customer Status'].unique(),
            default=df['Customer Status'].unique()
        )

    # Second row of filters
    col5, col6, col7 = st.columns(3)

    with col5:
        # Marital status filter
        married_filter = st.multiselect(
            "Select Marital Status",
            options=df['Married'].unique(),
            default=df['Married'].unique()
        )

    with col6:
        # Number of dependents filter
        dependents_filter = st.multiselect(
            "Select Number of Dependents",
            options=sorted(df['Number of Dependents'].unique()),
            default=sorted(df['Number of Dependents'].unique())
        )

# Apply filters
filter_conditions = [
    (df['Age'] >= min_age) & (df['Age'] <= max_age),
    df['Gender'].isin(gender_filter),
    df['Customer Status'].isin(status_filter),
    df['Married'].isin(married_filter),
    df['Number of Dependents'].isin(dependents_filter)
]

if 'Persona' in df.columns and len(persona_filter) > 0:
    filter_conditions.append(df['Persona'].isin(persona_filter))

filtered_df = df[np.all(filter_conditions, axis=0)]

##########################################
# Custom CSS for tabs
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 25px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 8px 8px 0px 0px;
        gap: 10px;
        font-weight: 400;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #DEE2E6;
    }

    .stTabs [aria-selected="true"] {
        background-color: #4B8DF8;
        color: white;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"]:hover {
        background-color: #3A7DE8;
    }
</style>
""", unsafe_allow_html=True)

# Create tabs with Overview as the first tab
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌐 Overview", 
    "📊 Gender Analysis", 
    "👨‍👩‍👧‍👦 Dependents Analysis", 
    "📈 Age Analysis",
    "⚠️ Churn Risk Analysis"
])

with tab1:
    st.subheader("Demographics Overview")

    # Create 2x2 subplot layout
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=["Gender", "Married", "Age", "Number of Dependents"],
        specs=[[{'type': 'domain'}, {'type': 'domain'}], [{'type': 'xy'}, {'type': 'xy'}]]
    )

    # Row 1 - Pie Charts
    fig.add_trace(go.Pie(labels=filtered_df['Gender'].value_counts().index,
                         values=filtered_df['Gender'].value_counts().values,
                         name="Gender"), row=1, col=1)

    fig.add_trace(go.Pie(labels=filtered_df['Married'].value_counts().index,
                         values=filtered_df['Married'].value_counts().values,
                         name="Married"), row=1, col=2)

    # Row 2 - Histograms
    fig.add_trace(go.Histogram(x=filtered_df['Age'], name="Age", marker_color='steelblue'), row=2, col=1)
    fig.add_trace(go.Histogram(x=filtered_df['Number of Dependents'], name="Number of Dependents", marker_color='steelblue'), row=2, col=2)

    # Layout
    fig.update_layout(
        title_text="Demographics Overview - Univariate scope",
        template='simple_white',
        showlegend=False,
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Gender and Marital Status Analysis")

    col1, col2 = st.columns(2)

    with col1:
        filtered_df['Married_Gender'] = filtered_df['Married'].replace({'Yes': 'Married', 'No': 'Single'}) + ' | ' + filtered_df['Gender']
        fig = px.histogram(filtered_df, x='Married_Gender', template='presentation', 
                          title='Customer Status by Gender and Marital Status', 
                          text_auto=True, color='Customer Status',
                          color_discrete_map=churn_color)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        status_matrix = pd.crosstab(filtered_df['Married_Gender'], filtered_df['Customer Status'], margins=True, margins_name='Total')
        st.dataframe(status_matrix.style.background_gradient(cmap='Blues'))

with tab3:
    st.subheader("Dependents Analysis")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(filtered_df, x='Number of Dependents', color='Married_Gender',
                          template='presentation', title='Dependents by Gender/Marital Status',
                          text_auto=True, marginal='box')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(filtered_df, x='Number of Dependents', color='Customer Status',
                          template='presentation', title='Dependents by Customer Status',
                          text_auto=True, marginal='box',
                          color_discrete_map=churn_color)
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Age Analysis")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(filtered_df, x='Age', template='presentation', 
                          title='Age Distribution by Gender/Marital Status', 
                          text_auto=True, color='Married_Gender', marginal='box')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(filtered_df, x='Age', template='presentation', 
                          title='Age Distribution by Customer Status', 
                          text_auto=True, color='Customer Status', marginal='box',
                          color_discrete_map=churn_color)
        st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.subheader("Churn Risk Analysis by Demographics")

    # Define bins and labels for Age_cluster
    bins = [18, 20, 30, 40, 50, 60, 70, 80, 90, 100, np.inf]
    labels = ['18', '20', '30', '40', '50', '60', '70', '80', '90', '100+']

    Demo_df = filtered_df.copy()
    Demo_df['Age_cluster_cut'] = pd.cut(Demo_df['Age'], bins=bins, labels=labels, right=False, include_lowest=True)
    Demo_df['aggre'] = (Demo_df['Married_Gender'].astype(str) + ' | ' + 
                       Demo_df['Age_cluster_cut'].astype(str) + ' | ' + 
                       Demo_df['Number of Dependents'].astype(str) + ' | ')

    churn_summary = Demo_df.groupby('aggre')['Customer Status'].value_counts().unstack(fill_value=0)
    churn_summary['Total'] = churn_summary.sum(axis=1)
    churn_summary['Churn%'] = ((churn_summary['Churned'] / churn_summary['Total']) * 100).round(1)

    # Add minimum group size filter
    min_group_size = st.slider("Minimum group size to include in analysis", 1, 50, 8, key='churn_slider')

    # Filter by group size
    churn_summary_filtered = churn_summary[churn_summary['Total'] >= min_group_size]

    # Display options
    view_option = st.radio("View churn analysis by:", 
                          ["Highest Churn%", "Highest Churn Count"],
                          horizontal=True)

    if view_option == "Highest Churn%":
        churn_summary_display = churn_summary_filtered.sort_values(by='Churn%', ascending=False).head(20)
        st.subheader("Top 20 Demographic Groups by Churn Percentage")
    else:
        churn_summary_display = churn_summary_filtered.sort_values(by='Churned', ascending=False).head(20)
        st.subheader("Top 20 Demographic Groups by Churn Count")

    # Add styling to the dataframe
    styled_df = churn_summary_display.style\
        .background_gradient(subset=['Churn%'], cmap='OrRd')\
        .background_gradient(subset=['Churned'], cmap='OrRd')\
        .format({'Churn%': "{:.1f}%"})

    st.dataframe(styled_df)

    # Add download button
    st.download_button(
        label="Download Churn Analysis Data",
        data=churn_summary_display.to_csv().encode('utf-8'),
        file_name='demographic_churn_analysis.csv',
        mime='text/csv',
        key='churn_download'
    )
