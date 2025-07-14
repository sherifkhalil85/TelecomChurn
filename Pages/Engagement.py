import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# ------------------ Setup ------------------
churn_color = {'Joined': '#2ca02c', 'Stayed': '#1f77b4', 'Churned': '#ff7f0e'}

st.set_page_config(
    page_title="Engagement Analysis",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_data
def load_data():
    return pd.read_csv("telecom_customer_churn_clustered.csv")

df = load_data()

# Create derived field for service class
df = df.copy()
df['ser_class'] = df['Phone Service'] + ' | ' + df['Internet Service']
df['ser_class'] = df['ser_class'].map({
    'Yes | Yes': 'Both',
    'Yes | No': 'phone only',
    'No | Yes': 'Internet Only'
})



# ------------------ header ------------------
st.title("Customer Engagement Analysis")

# ------------------ Filters ------------------
with st.expander("Filter Options", expanded=False):
    selected_status = st.multiselect("Select Customer Status", df['Customer Status'].unique(), default=list(df['Customer Status'].unique()))
    selected_persona = st.multiselect("Select Persona", df['Persona'].unique(), default=list(df['Persona'].unique()))
    df = df[df['Customer Status'].isin(selected_status) & df['Persona'].isin(selected_persona)]


# ---------------- Analysis -----------------
engagement_features = ['Offer', 'Number of Referrals', 'Tenure in Months']
engag_out = df.copy()

# ------------------ Descriptive Summary ------------------
show_desc = st.checkbox("Show Descriptive Summary", value=False)

if show_desc:
    st.subheader("Descriptive Summary")

    st.markdown("**📊 Numeric Features**")
    st.dataframe(df[engagement_features].describe().round(2).T)

    st.markdown("**📋 Categorical Feature: Offer**")
    st.dataframe(df['Offer'].describe().to_frame().T)


# ------------------ Univariate and Bivariate ------------------
st.subheader("Distribution Analysis")


status_order = ['Churned', 'Stayed', 'Joined']  # Ensure consistent category order

nrows = len(engagement_features)
fig = make_subplots(
    rows=nrows, cols=2,
    subplot_titles=[
        f"Uni-variate: {f}" if i % 2 == 0 else f"Bi-variate: {f}"
        for f in engagement_features for i in range(2)
    ],
    vertical_spacing=0.08,
    horizontal_spacing=0.05
)

for i, feature in enumerate(engagement_features):
    row = i + 1

    # Uni-variate plot (all data)
    fig.add_trace(
        go.Histogram(
            x=df[feature],
            name=f'{feature} Distribution',
            marker_color='#1f77b4',  # 🔹 Default blue color
            showlegend=False
        ),
        row=row, col=1
    )


    # Bi-variate plot (by churn status)
    for status in status_order:
        if status not in df['Customer Status'].unique():
            continue
        fig.add_trace(
            go.Histogram(
                x=df[df['Customer Status'] == status][feature],
                name=status,
                marker_color=churn_color.get(status, None),
                legendgroup='Customer Status Group',
                showlegend=(i == 0)
            ),
            row=row, col=2
        )


# Final layout
fig.update_layout(
    barmode='group',
    title_text="Engagement Features: Uni-variate and Bi-variate Analysis",
    template='simple_white',
    height=300 * nrows,
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)


# ------------------ Tenure vs Features ------------------
st.subheader("Tenure by Engagement Features")
features = ['ser_class', 'Sub_Services', 'Offer', 'Number of Referrals']
n = len(features)
ncols = 2
nrows = (n + ncols - 1) // ncols

fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(18, 5 * nrows))
axes = axes.flatten() if n > 1 else [axes]
handles, labels = None, None

for i, feature in enumerate(features):
    sns.boxplot(x=feature, y='Tenure in Months', data=df, hue='Customer Status', palette=churn_color, ax=axes[i])
    axes[i].set_title(f'Tenure vs {feature}')
    if i == 0:
        handles, labels = axes[i].get_legend_handles_labels()
    axes[i].legend_.remove()

for j in range(i + 1, len(axes)):
    axes[j].axis('off')

fig.suptitle('Tenure for Main Services and Engagement View', fontsize=18, y=1.02)
fig.legend(handles, labels, loc='upper right', bbox_to_anchor=(1.0, 1.0))
plt.tight_layout(rect=[0, 0, 1, 0.98])
st.pyplot(fig)

# ------------------ Correlation Analysis ------------------
st.subheader("Correlation with Tenure")
df1 = df[df['Sub_Services'] >= 1]
sub_corr = df1['Sub_Services'].corr(df1['Tenure in Months'])
ref_corr = df1['Number of Referrals'].corr(df1['Tenure in Months'])

st.markdown(f"- **Correlation between 'Sub_Services' and 'Tenure'**: `{sub_corr:.2f}`")
st.markdown(f"- **Correlation between 'Referrals' and 'Tenure'**: `{ref_corr:.2f}`")
