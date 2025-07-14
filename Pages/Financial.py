import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# ------------------ Setup ------------------
churn_color = {'Joined': '#2ca02c', 'Stayed': '#1f77b4', 'Churned': '#ff7f0e'}

st.set_page_config(
    page_title="Financial Analysis",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_data
def load_data():
    return pd.read_csv("Data/telecom_customer_churn_clustered.csv")

df = load_data()

# ------------------ Page Title ------------------
st.title("💰 Financial Performance Overview")
st.markdown("Analyze financial impact by churn status, with a focus on monthly revenue, losses, and retention effectiveness.")

# ------------------ Data Preparation ------------------
monthly_charge_features = ['Current Monthly Charge', 'Average_Monthly_Charge',
                           'Total Refunds', 'Total Charges', 'Net_Revenue']

fin_sum = df.groupby('Customer Status')[monthly_charge_features].sum().round(1).T
fin_sum['total'] = fin_sum.sum(axis=1)

# Calculate key metrics
fin_sum['current'] = fin_sum['total'] - fin_sum.get('Churned', 0)
fin_sum['loss'] = fin_sum.get('Churned', 0)
fin_sum['Recover%'] = ((fin_sum.get('Joined', 0) / fin_sum['total']) * 100).round(1)
fin_sum['old%'] = ((fin_sum.get('Stayed', 0) / fin_sum['total']) * 100).round(1)
fin_sum['loss%'] = ((fin_sum.get('Churned', 0) / fin_sum['total']) * 100).round(1)
fin_sum['active%'] = 100 - fin_sum['loss%']

# ------------------ Format Helpers ------------------
def format_money(val):
    if pd.isnull(val):
        return ""
    if abs(val) >= 1_000_000:
        return f"${val/1_000_000:.1f}M"
    elif abs(val) >= 1_000:
        return f"${val/1_000:.1f}K"
    else:
        return f"${val:.0f}"

def format_percent(val):
    return f"{val:.1f}%" if pd.notnull(val) else ""

# ------------------ Insights Summary ------------------
st.subheader("🧾 Financial Summary Insights")

# Extract values for Current Monthly Charge
cmc_loss_val = fin_sum.loc['Current Monthly Charge', 'loss']
cmc_loss_pct = fin_sum.loc['Current Monthly Charge', 'loss%']
cmc_join_val = fin_sum.loc['Current Monthly Charge', 'Joined']
cmc_join_pct = fin_sum.loc['Current Monthly Charge', 'Recover%']
cmc_NetLoss_val = cmc_loss_val - cmc_join_val
cmc_NetLoss_pct = cmc_loss_pct - cmc_join_pct

# Display insights in bordered box
st.markdown(f"""
<div style="
    border: 2px solid #ccc;
    border-radius: 10px;
    padding: 20px;
    margin-top: 10px;
    background-color: #f9f9f9;
    font-size: 16px;
    line-height: 1.6;
">
<ol>
  <li><strong>Current Monthly Charge</strong>:
    <ul>
      <li>A. Loss is <strong>{format_percent(cmc_loss_pct)}</strong> (<em>{format_money(cmc_loss_val)}</em>).</li>
      <li>B. New customers contribute only <strong>{format_percent(cmc_join_pct)}</strong> (<em>{format_money(cmc_join_val)}</em>), which is <strong>not sufficient</strong> to offset lost revenue from churned customers.</li>
      <li>C. <strong>Monthly Net Loss</strong> is <strong>{format_percent(cmc_NetLoss_pct)}</strong> (<em>{format_money(cmc_NetLoss_val)}</em>).</li>
    </ul>
  </li>
  <li>⚠️ <strong>Note:</strong> While <em>Total Charges</em> and <em>Net Revenue</em> from new customers may appear high, they’re likely <strong>inflated</strong> due to short tenure (&lt; 3 months).</li>
</ol>
</div>
""", unsafe_allow_html=True)

# ------------------ Financial Summary Table ------------------
st.subheader("📊 Aggregated Financial Summary by Customer Status")

styled_table = fin_sum.style \
    .format({
        'Churned': format_money,
        'Stayed' : format_money,
        'Joined': format_money,
        'total': format_money,
        'current': format_money,
        'loss': format_money,
        'Recover%': format_percent,
        'old%': format_percent,
        'loss%': format_percent,
        'active%': format_percent
    }) \
    .background_gradient(subset=['total', 'current'], cmap='Greens') \
    .background_gradient(subset=['loss'], cmap='Reds') \
    .highlight_max(axis=0, subset=['Recover%', 'old%', 'active%'], color='lightgreen') \
    .highlight_max(axis=0, subset=['loss%'], color='salmon') \
    .set_properties(**{
        'text-align': 'center',
        'font-weight': 'bold',
        'border-color': 'gray',
        'border-width': '1px',
        'border-style': 'solid'
    }) \
    .set_table_styles([{
        'selector': 'th',
        'props': [('font-size', '14px'), ('background-color', '#f2f2f2')]
    }])

st.dataframe(styled_table, use_container_width=True)

# ------------------ Revenue Distribution Chart ------------------
st.subheader("💹 Revenue Distribution (Loss vs Current Value)")

fig_val = px.histogram(
    fin_sum.reset_index(),
    x='index',
    y=['total', 'loss', 'current'],
    barmode='group',
    text_auto=True,
    template='presentation'
)
fig_val.update_layout(xaxis_title="Financial Metric", yaxis_title="Amount", legend_title_text="Category")
st.plotly_chart(fig_val, use_container_width=True)

# ------------------ Financial Contribution Breakdown ------------------
st.subheader("📈 Financial Contribution Breakdown (%)")

fig_pct = px.histogram(
    fin_sum.reset_index(),
    x='index',
    y=['old%', 'loss%', 'Recover%'],
    barmode='stack',
    text_auto=True,
    template='presentation'
)
fig_pct.update_layout(xaxis_title="Financial Metric", yaxis_title="Percentage", legend_title_text="Status %")
st.plotly_chart(fig_pct, use_container_width=True)
