
import pandas as pd
import plotly.express as px
import streamlit as st

# ------------------ Setup ------------------


st.set_page_config(
    page_title="Churn Feature Analysis",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_data
def load_data():
    return pd.read_csv("telecom_customer_churn_clustered.csv")

df = load_data()

# ------------------ Title ------------------
st.title("📉 Churn Drivers Analysis")
st.markdown("Breakdown of churn categories, root causes, tenure impact, and strategic recommendations.")

# ------------------ Data Preparation ------------------
churn_df = df[df['Churn'] == 1]

# ------------------ Churn Summary ------------------
churn_rate = (len(churn_df) / len(df)) * 100

st.markdown(f"""
**Total Customers:** {len(df):,}  
**Churned Customers:** {len(churn_df):,} (**{churn_rate:.1f}%**)
""")

# ------------------ Churn Category Distribution ------------------

st.subheader("🔹 Churn Root Cause - Category & Sub-Category")

# Split layout into two columns
col1, col2 = st.columns([2, 1])  # 2:1 ratio for better space

with col1:
    fig_cat = px.histogram(
        churn_df,
        x='Churn Category',
        color='Churn Category',
        template='presentation',
        text_auto=True,
        title="Churn Breakdown by Category",
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    churn_cat_counts = churn_df['Churn Category'].value_counts().reset_index()
    churn_cat_counts.columns = ['Churn Category', 'Count']

    fig_pie = px.pie(
        churn_cat_counts,
        values='Count',
        names='Churn Category',
        title="Churn Category % Share",
        template='presentation',
        color='Churn Category',
        hole=0.4  # donut chart
    )
    fig_pie.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

# ------------------ Churn Reasons ------------------

churn_reasons = churn_df.groupby(['Churn Category', 'Churn Reason'])['Churn'].count().reset_index()
churn_reasons = churn_reasons.sort_values(by='Churn', ascending=False)
fig_reason = px.histogram(
    churn_reasons, x='Churn Reason', y='Churn',
    color='Churn Category', text_auto=True, template='presentation',
    title= 'Churn Breakdown'

)
fig_reason.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig_reason, use_container_width=True)


# ------------------ Offer vs Churn Category ------------------

st.subheader("🎯 Churned Offers by Category")
churn_offer = churn_df.groupby(['Offer', 'Churn Category'])['Churn'].count().reset_index()
churn_offer = churn_offer.sort_values(by='Churn', ascending=False)
fig_offer = px.bar(
    churn_offer, x='Offer', y='Churn', color='Churn Category',
    barmode='group', text_auto=True, template='presentation',

)
st.plotly_chart(fig_offer, use_container_width=True)


# ------------------ Attitude Tenure ------------------

st.subheader("🧭 Tenure Distribution: Attitude Churn")
att_chur = churn_df[churn_df['Churn Category'] == 'Attitude']

fig1= px.histogram(
    att_chur, x='Tenure in Months',
    template='presentation', title="Tenure Distribution - Attitude Churn"
)
st.plotly_chart(fig1, use_container_width=True)

fig2= px.histogram(
    att_chur, x='Tenure in Months',
    facet_col='Churn Reason', template='presentation',
    title="Tenure vs Reason (Attitude Churn)"
)
st.plotly_chart(fig2, use_container_width=True)

# ------------------ Insights & Recommendations ------------------
st.subheader("📌 Key Insights & Strategic Recommendations")

st.markdown("""
<div style="
    border: 2px solid #dcdcdc;
    border-radius: 12px;
    padding: 20px;
    margin-top: 10px;
    background-color: #f9f9f9;
    box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease-in-out;
    font-size: 16px;
    line-height: 1.6;
">
<h4>📉 Churn Analysis Summary</h4>
<ol>
<li><strong>Competitor (44%)</strong>
    <ul>
        <li>Most churned users had <strong>no offer</strong> or entry-level <strong>Offer E</strong>.</li>
        <li>Key reasons: <em>Better Devices</em>, <em>Better Offers</em>.</li>
        <li>👉 Device availability and offer structure need urgent review.</li>
    </ul>
</li>
<li><strong>Dissatisfaction (17%)</strong>
    <ul>
        <li>Main causes: Product/Service issues, and sometimes support quality.</li>
    </ul>
</li>
<li><strong>Attitude (17%)</strong>
    <ul>
        <li>Found mostly in <strong>new customers</strong>, indicating weak onboarding/support.</li>
    </ul>
</li>
<li><strong>Price (11%)</strong>
    <ul>
        <li>Perceived <strong>high cost</strong> without added value.</li>
    </ul>
</li>
</ol>

<hr style="margin:10px 0;">

<h4>✅ Recommendations</h4>
<ol>
<li>🔁 <strong>Redesign Offers</strong>
    <ul>
        <li>Especially <strong>Offer E</strong>.</li>
        <li>Audit device portfolio and improve upgrade availability.</li>
    </ul>
</li>
<li>🛠️ <strong>Enhance Support & Product Quality</strong>
    <ul>
        <li>Act on service complaints.</li>
        <li>Train agents in empathy and retention handling.</li>
    </ul>
</li>
<li>🤝 <strong>Dedicated New Customer Handling</strong>
    <ul>
        <li>Assign top agents to early-tenure customers.</li>
        <li>Create welcome programs or dedicated onboarding support lines.</li>
    </ul>
</li>
<li>💸 <strong>Reevaluate Pricing Strategy</strong>
    <ul>
        <li>Benchmark against competitors.</li>
        <li>Build flexible bundles or loyalty-based rewards.</li>
    </ul>
</li>
</ol>
</div>
""", unsafe_allow_html=True)
