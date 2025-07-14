import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Color schemes
churn_color = {'Joined': '#2ca02c', 'Stayed': '#1f77b4', 'Churned': '#ff7f0e'}

# Page config
st.set_page_config(
    page_title="Service Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    return pd.read_csv('telecom_customer_churn_clustered.csv')

df = load_data()

# Feature list
features = ['Online Security', 'Online Backup', 'Device Protection Plan',
            'Premium Tech Support', 'Streaming TV', 'Streaming Movies',
            'Streaming Music', 'Unlimited Data']

# Service class
serv_df = df.copy()
serv_df['ser_class'] = serv_df['Phone Service'] + ' | ' + serv_df['Internet Service']
serv_df['ser_class'] = serv_df['ser_class'].map({'Yes | Yes': 'Both', 'Yes | No': 'Phone Only', 'No | Yes': 'Internet Only'})

# Page title
st.title("📡 Service Subscribers Analysis")

# Filter UI in expander
with st.expander("🔎 Filter Options", expanded=False):
    persona_list = serv_df['Persona'].dropna().unique().tolist()
    selected_personas = st.multiselect("Select Persona(s):", persona_list, default=persona_list)

    service_classes = serv_df['ser_class'].dropna().unique().tolist()
    selected_services = st.multiselect("Select Main Service(s):", service_classes, default=service_classes)

# Filtered Data
filtered_df = serv_df[
    (serv_df['Persona'].isin(selected_personas)) &
    (serv_df['ser_class'].isin(selected_services))
]

# Top metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("% Phone Service", f"{(filtered_df['Phone Service'] == 'Yes').mean() * 100:.1f}%")
with col2:
    st.metric("% Internet Service", f"{(filtered_df['Internet Service'] == 'Yes').mean() * 100:.1f}%")
with col3:
    st.metric("% Both Services", f"{(filtered_df['ser_class'] == 'Both').mean() * 100:.1f}%")

# Pie chart distribution
fig = make_subplots(rows=1, cols=3, specs=[[{'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}]],
                    subplot_titles=['Phone Service', 'Internet Service', 'Combined Service Type'])
cols = ['Phone Service', 'Internet Service', 'ser_class']
for i, s in enumerate(cols):
    service_counts = filtered_df[s].value_counts().reset_index()
    service_counts.columns = [s, 'count']
    fig.add_trace(go.Pie(labels=service_counts[s], values=service_counts['count'], name=s), row=1, col=i+1)
fig.update_layout(title_text='Phone vs Internet Service Subscription Distribution', template='presentation')
st.plotly_chart(fig, use_container_width=True)

# Customer status distribution by service class (%)
fig = px.histogram(filtered_df, x='ser_class', color='Customer Status',
                   template='simple_white', barmode='stack',
                   text_auto=True, color_discrete_map=churn_color,
                   title='Customer Status Distribution by Service Class (%)')
st.plotly_chart(fig, use_container_width=True)

# Sub header
st.subheader("📦 Additional Services")

# Histogram for Sub_Services by ser_class
fig = px.histogram(filtered_df, x='Sub_Services', color='ser_class',
                   title='Sub-Services Count by Service Class', template='presentation', text_auto=True)
st.plotly_chart(fig, use_container_width=True)

# Sub-service summary
summary = pd.DataFrame()
for feature in features:
    counts = filtered_df[feature].value_counts()
    summary.loc[feature, 'Yes'] = counts.get('Yes', 0)
    summary.loc[feature, 'No'] = counts.get('No', 0)
    summary.loc[feature, 'no_internet_service'] = counts.get('no_internet_service', 0)
summary = summary.astype(int).reset_index().rename(columns={'index': 'Service Feature'})
summary['Subscriber %'] = summary['Yes'] / len(filtered_df)

# Stacked bar chart for service feature adoption
fig = px.bar(summary, 
             x='Service Feature', 
             y=['Yes', 'No', 'no_internet_service'],
             title='Subscription Status by Service Feature (Stacked)',
             template='simple_white', barmode='stack', text_auto=True)
st.plotly_chart(fig, use_container_width=True)

# Melted long format for feature churn analysis
long_df = filtered_df.melt(id_vars=['Customer Status', 'Persona'], value_vars=features,
                           var_name='Feature', value_name='Value')
long_df = long_df[long_df['Value'] == 'Yes']

# Feature vs churn grouped
fig = px.histogram(long_df, x='Feature', color='Customer Status',
                   barmode='stack', template='simple_white', color_discrete_map=churn_color,
                   text_auto=True, facet_col='Persona',
                   title='Subscriptions by Feature & Customer Status per Persona')
st.plotly_chart(fig, use_container_width=True)

# Churn % per feature by persona
count_df = long_df.groupby(['Feature', 'Customer Status', 'Persona']).size().reset_index(name='Count')
count_df['Percent'] = count_df.groupby(['Feature', 'Persona'])['Count'].transform(lambda x: 100 * x / x.sum())
churned_ser_df = count_df[count_df['Customer Status'] == 'Churned']
fig = px.bar(churned_ser_df, x='Feature', y='Percent', color='Persona', barmode='group',
             text=churned_ser_df['Percent'].round(1).astype(str) + '%',
             template='simple_white', title='Churned Percentage per Feature by Persona')
fig.update_traces(textposition='inside')
fig.update_layout(yaxis_title='Percentage', yaxis_tickformat='%')
st.plotly_chart(fig, use_container_width=True)
