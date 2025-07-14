import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ------------------ Setup ------------------
churn_color = {'Joined': '#2ca02c', 'Stayed': '#1f77b4', 'Churned': '#ff7f0e'}

st.set_page_config(
    page_title="Billing & Contract Analysis",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_data
def load_data():
    return pd.read_csv("Data/telecom_customer_churn_clustered.csv")

df = load_data()

# ------------------ Page Title ------------------
st.title("📑 Billing & Contract Analysis")
st.markdown("Explore how different billing-related features affect customer churn behavior.")

# ------------------ Filters ------------------
with st.expander("🔍 Filter Options", expanded=False):
    selected_status = st.multiselect(
        "Select Customer Status", 
        options=df['Customer Status'].unique(), 
        default=df['Customer Status'].unique()
    )

    selected_contracts = st.multiselect(
        "Select Contract Types", 
        options=df['Contract'].unique(), 
        default=df['Contract'].unique()
    )

    selected_payment = st.multiselect(
        "Select Payment Methods", 
        options=df['Payment Method'].unique(), 
        default=df['Payment Method'].unique()
    )

# Apply filters
df_filtered = df[
    (df['Customer Status'].isin(selected_status)) &
    (df['Contract'].isin(selected_contracts)) &
    (df['Payment Method'].isin(selected_payment))
]

# ------------------ Contract vs Payment Crosstab ------------------
st.subheader("📋 Contract vs. Payment Method Summary")
relationship_counts = pd.crosstab(df_filtered['Contract'], df_filtered['Payment Method'])
st.dataframe(relationship_counts.style.background_gradient(cmap="Blues"))

# ------------------ Univariate & Bivariate Plots ------------------
st.subheader("📊 Uni-variate and Bi-variate Analysis")

contract_billing_features = ['Contract', 'Paperless Billing', 'Payment Method']
nrows = len(contract_billing_features)
ncols = 2

fig = make_subplots(
    rows=nrows,
    cols=ncols,
    subplot_titles=[
        f'Uni-variate: {feat}' if j % 2 == 0 else f'Bi-variate: {feat}'
        for i in range(nrows) for j, feat in enumerate([contract_billing_features[i], contract_billing_features[i]])
    ],
    vertical_spacing=0.08,
    horizontal_spacing=0.05
)

for i, feature in enumerate(contract_billing_features):
    row_num = i + 1

    # Univariate
    fig.add_trace(
        go.Histogram(
            x=df_filtered[feature],
            name=f'{feature} Distribution',
            marker_color='#1f77b4',
            showlegend=False
        ),
        row=row_num, col=1
    )


    # Bivariate
    for j, status in enumerate(df_filtered['Customer Status'].unique()):
        fig.add_trace(
            go.Histogram(
                x=df_filtered[df_filtered['Customer Status'] == status][feature],
                name=status,
                marker_color=churn_color.get(status),
                legendgroup='Customer Status Group',
                showlegend=True if i == 0 else False
            ),
            row=row_num, col=2
        )


fig.update_layout(
    barmode='group',
    title_text="Contract & Billing Feature Analysis",
    template='simple_white',
    height=280 * nrows,
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

# ------------------ Combined Contract + Payment Method ------------------
st.subheader("🔗 Combined Contract and Payment Method Analysis")

contr_df = df_filtered.copy()
contr_df['aggreg'] = contr_df['Contract'] + ' | ' + contr_df['Payment Method']

fig_combined = px.histogram(
    contr_df,
    x='aggreg',
    color='Customer Status',
    color_discrete_map=churn_color,
    template='simple_white',
    title="Contract-Payment Combinations by Customer Status",text_auto = True
)
fig_combined.update_layout(xaxis_title="Contract + Payment Method", yaxis_title="Count")
st.plotly_chart(fig_combined, use_container_width=True)

# ------------------ Senior Customers & Traditional Methods ------------------
st.subheader("📮 Senior Customers & Traditional Payment Methods")
st.markdown("**Checking if senior customers still prefer mailing as a payment method.**")

fig_age = px.histogram(
    df_filtered,
    x='Age',
    color='Payment Method',
    facet_col='Payment Method',
    template='simple_white',
    height=500
)
fig_age.update_layout(xaxis_title="Age", yaxis_title="Count")
st.plotly_chart(fig_age, use_container_width=True)
