import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Color schemes
churn_color = {'Joined':'#2ca02c', 'Stayed':'#1f77b4', 'Churned':'#ff7f0e'}

Persona_color_map = {
    "A - Premium Loyal Customers": "#2ca02c",     # Green (very positive)
    "B - Balanced Bundle Seekers": "#1f77b4",      # Blue (positive)
    "C - Data-Capped Digitals": "#EBCA48",         # Yellow (neutral to mild concern)
    "D - Legacy Phone-Only Users": "#ff7f0e",      # Orange (negative)
    "E - Churn-Risk New Users": "#d62728"          # Red (most negative)
}

# Page config
st.set_page_config(
    page_title="Customer Persona Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    df = pd.read_csv('telecom_customer_churn_clustered.csv')
    return df

df = load_data()

# Define features
numeric_features = [
    'Age', 'Number of Referrals', 'Tenure in Months',
    'Avg Monthly Long Distance Charges', 'Avg Monthly GB Download',
    'Current Monthly Charge', 'Total Charges', 'Total Refunds',
    'Total Extra Data Charges', 'Total Long Distance Charges',
    'Total Revenue', 'Average_Monthly_Charge', 'Net_Revenue'
]

categorical_features = [
    'Married', 'Number of Dependents', 'Offer', 'Phone Service',
    'Multiple Lines', 'Internet Service', 'Internet Type',
    'Online Security', 'Online Backup', 'Device Protection Plan',
    'Premium Tech Support', 'Streaming TV', 'Streaming Movies',
    'Streaming Music', 'Unlimited Data', 'Contract',
    'Paperless Billing', 'Payment Method', 'Sub_Services',
    'Married_Gender'
]

def show_persona_page():
    st.title("Customer Persona Analysis")
    st.markdown("""
    Analyze customer segments (personas) to understand their characteristics, behaviors, 
    and churn patterns. Identify high-risk groups and opportunities for targeted retention strategies.
    """)



    # ------------------ Persona Distribution ------------------
    st.subheader("Persona Distribution")
    persona_counts = df['Persona'].value_counts().reset_index()
    persona_counts.columns = ['Persona', 'Count']
    persona_counts['Percentage'] = (persona_counts['Count'] / persona_counts['Count'].sum() * 100).round(1)


    col1, col2 = st.columns(2)

    with col1:
        # Pie chart
        fig_pie = px.pie(persona_counts, values='Count', names='Persona', 
                        color='Persona', color_discrete_map=Persona_color_map,
                        hole=0.3)
        fig_pie.update_traces(textposition='inside', 
                            textinfo='percent+label',
                            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}</br>")
        fig_pie.update_layout(showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Bar chart
        fig_bar = px.bar(persona_counts, x='Persona', y='Count', color='Persona',
                        color_discrete_map=Persona_color_map,
                        text='Count',
                        title='Customer Count by Persona')
        fig_bar.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig_bar.update_layout(
            xaxis_title='Persona',
            yaxis_title='Customer Count',
            showlegend=False,
            hovermode="x unified"
        )
        fig_bar.update_traces(
            hovertemplate="<b>%{x}</b><br>Count: %{y:,}</br>"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ------------------ Churn Rate by Persona ------------------
    st.subheader("📉 Churn Rate by Persona")
    df_grouped = df.groupby(['Persona', 'Customer Status']).size().reset_index(name='Count')
    df_pivot = df_grouped.pivot_table(index='Persona', columns='Customer Status', values='Count', fill_value=0)

    # Ensure all expected statuses are present
    for col in ['Stayed', 'Churned', 'Joined']:
        if col not in df_pivot.columns:
            df_pivot[col] = 0

    # Calculate totals and churn percentage
    df_pivot['Total'] = df_pivot[['Stayed', 'Churned', 'Joined']].sum(axis=1)
    df_pivot['Churn%'] = ((df_pivot['Churned'] / df_pivot['Total']) * 100).round(2)
    df_pivot = df_pivot.reset_index()

    # Format and style the table without index
    styled_churn = df_pivot[['Persona', 'Stayed', 'Churned', 'Joined', 'Total', 'Churn%']] \
        .sort_values('Churn%', ascending=False) \
        .style.format({
            'Stayed': '{:,}',
            'Churned': '{:,}',
            'Joined': '{:,}',
            'Total': '{:,}',
            'Churn%': '{:.1f}%'
        }) \
        .highlight_max(subset=['Churn%'], color='salmon') \
        .highlight_min(subset=['Churn%'], color='lightgreen') \
        .set_properties(**{
            'text-align': 'center',
            'border': '1px solid #ddd'
        }) \
        .set_table_styles([{
            'selector': 'th',
            'props': [('font-size', '12px'), ('background-color', '#f7f7f9')]
        }])

    # Show styled table without index
    st.dataframe(styled_churn.hide(axis='index'), use_container_width=True)

    # Prepare for plotting
    status_order = ['Stayed', 'Churned', 'Joined']
    df_melted = df_pivot.melt(id_vars='Persona', value_vars=status_order, 
                             var_name='Customer Status', value_name='Count')

    # Create two columns for side-by-side visualizations
    col1, col2 = st.columns(2)

    with col1:
        # Stacked bar chart with enhanced tooltips
        fig_churn = px.bar(df_melted, x='Persona', y='Count', color='Customer Status',
                         barmode='stack', template='presentation', text_auto=True,
                         title='Churn Distribution by Persona',
                         color_discrete_map=churn_color)
        fig_churn.update_layout(
            xaxis_tickangle=30,
            hovermode="x unified",
            hoverlabel=dict(bgcolor="white", font_size=12)
        )
        fig_churn.update_traces(
            hovertemplate="<b>%{x}</b><br>Status: %{fullData.name}<br>Count: %{y}</br>"
        )

        # Add annotation for highest churn group
        max_churn = df_pivot.loc[df_pivot['Churn%'].idxmax()]
        fig_churn.add_annotation(
            x=max_churn['Persona'],
            y=max_churn['Churned'],
            text=f"Highest Churn: {max_churn['Churn%']}%",
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-40
        )
        st.plotly_chart(fig_churn, use_container_width=True)

    with col2:
        # Churn rate bar chart with enhanced tooltips and annotations
        fig_rate = px.bar(df_pivot, x='Persona', y='Churn%', color='Persona',
                         color_discrete_map=Persona_color_map,
                         title='Churn Rate by Persona',
                         text='Churn%')
        fig_rate.update_traces(
            texttemplate='%{text:.1f}%', 
            textposition='outside',
            hovertemplate="<b>%{x}</b><br>Churn Rate: %{y:.1f}%</br>"
        )
        fig_rate.update_layout(
            yaxis_title='Churn Rate (%)',
            showlegend=False,
            hovermode="x unified"
        )

        # Add average line and annotation
        avg_churn = df_pivot['Churn%'].mean()
        fig_rate.add_hline(
            y=avg_churn,
            line_dash="dot",
            line_color="Blue",
            annotation_font_color="#1f77b4",
            annotation_text=f"Average: {avg_churn:.1f}%",
            annotation_position="bottom right"
        )
        st.plotly_chart(fig_rate, use_container_width=True)

    # __________________Feature analysis________________________
    st.subheader("Persona Characteristics")

    # ------------------------Numerical features--------------------------------
    st.markdown("#### Numerical Features Distribution")
    selected_num_feature = st.selectbox("Select numerical feature:", numeric_features, key='num_feature_select')
    fig = px.box(df, y=selected_num_feature, color='Persona', 
                 color_discrete_map=Persona_color_map,
                 title=f'{selected_num_feature} Distribution by Persona')
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Value: %{y}</br>"
    )
    st.plotly_chart(fig, use_container_width=True)

    # -----------------------Categorical features-------------------------------
    st.markdown("#### Categorical Features Distribution")
    selected_cat_feature = st.selectbox("Select categorical feature:", categorical_features, key='cat_feature_select')
    fig = px.histogram(df, x=selected_cat_feature, color='Persona', 
                       color_discrete_map=Persona_color_map,
                       barmode='group',text_auto=True,
                       title=f'{selected_cat_feature} Distribution by Persona')
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Count: %{y}</br>"
    )
    st.plotly_chart(fig, use_container_width=True)

    # -----------------------Revenue analysis-----------------------------
    # Revenue Analysis Section
    st.subheader("Revenue Analysis by Persona")
    col1, col2 = st.columns(2)

    with col1:
        # Average Total Charges by Persona
        if 'Total Charges' in df.columns:
            avg_total = df['Total Charges'].mean()
            fig = px.bar(df.groupby('Persona')['Total Charges'].mean().reset_index(), 
                        x='Persona', 
                        y='Total Charges',
                        color='Persona',
                        color_discrete_map=Persona_color_map,
                        title='Average Total Charges by Persona')
            fig.update_traces(
                texttemplate='$%{y:,.2f}',
                textposition='outside',
                hovertemplate="<b>%{x}</b><br>Avg Total Charges: $%{y:,.2f}</br>"
            )
            fig.update_layout(
                yaxis_title='Amount ($)',
                showlegend=False
            )
            # Add blue average line annotation
            fig.add_hline(
                y=avg_total,
                line_dash="dash",
                line_color="#1f77b4",  # Blue color
                line_width=2,
                annotation_text=f"Overall Avg: ${avg_total:,.2f}",
                annotation_position="bottom right",
                annotation_font_size=12,
                annotation_font_color="#1f77b4",  # Blue color
                annotation_bgcolor="white",
                annotation_bordercolor="#1f77b4"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("'Total Charges' data not available")

    with col2:
        # Average Monthly Charges by Persona
        if 'Current Monthly Charge' in df.columns:
            avg_monthly = df['Current Monthly Charge'].mean()
            fig = px.bar(df.groupby('Persona')['Current Monthly Charge'].mean().reset_index(), 
                        x='Persona', 
                        y='Current Monthly Charge',
                        color='Persona',
                        color_discrete_map=Persona_color_map,
                        title='Average Monthly Charges by Persona')
            fig.update_traces(
                texttemplate='$%{y:,.2f}',
                textposition='outside',
                hovertemplate="<b>%{x}</b><br>Avg Monthly Charge: $%{y:,.2f}</br>"
            )
            fig.update_layout(
                yaxis_title='Amount ($)',
                showlegend=False
            )
            # Add blue average line annotation
            fig.add_hline(
                y=avg_monthly,
                line_dash="dash",
                line_color="#1f77b4",  # Blue color
                line_width=2,
                annotation_text=f"Overall Avg: ${avg_monthly:,.2f}",
                annotation_position="bottom right",
                annotation_font_size=12,
                annotation_font_color="#1f77b4",  # Blue color
                annotation_bgcolor="white",
                annotation_bordercolor="#1f77b4"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("'Current Monthly Charge' data not available")

    # -------------------------------Simplified Services adoption---------------------
    st.subheader("Service Bundle Adoption by Persona")

    # Create service classification
    serv_df = df.copy()
    serv_df['ser_class'] = serv_df['Phone Service'] + ' | ' + serv_df['Internet Service']
    serv_df['ser_class'] = serv_df['ser_class'].map({
        'Yes | Yes': 'Both',
        'Yes | No': 'Phone Only',
        'No | Yes': 'Internet Only',
        'No | No': 'None'
    })

    # Calculate adoption rates
    service_adoption = serv_df.groupby(['Persona', 'ser_class']).size().unstack().fillna(0)
    service_adoption = service_adoption.div(service_adoption.sum(axis=1), axis=0) * 100
    service_adoption = service_adoption.round(1).reset_index()

    # Melt for visualization
    service_adoption_melted = service_adoption.melt(id_vars='Persona', 
                                                   var_name='Service Bundle', 
                                                   value_name='Percentage')

    # Plot
    fig = px.bar(service_adoption_melted, 
                 x='Persona', 
                 y='Percentage', 
                 color='Service Bundle',
                 barmode='stack',
                 title='Service Bundle Adoption by Persona',
                 text='Percentage',
                 color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])

    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='inside',
        hovertemplate="<b>%{x}</b><br>Service: %{fullData.name}<br>Percentage: %{y:.1f}%</br>"
    )

    fig.update_layout(
        yaxis_title='Percentage (%)',
        xaxis_title='Persona',
        legend_title='Service Bundle'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Add this section after the Service Bundle Adoption section and before the if __name__ block

    # ----------------------- Cluster Insights ------------------------------
    st.subheader("📊 Persona Insights & Strategies")

    with st.expander("A - Premium Loyal Customers", expanded=False):
        st.markdown("""
        **Key Characteristics:**
        - Longest average tenure (58.29 months)
        - Highest total revenue ($6,849)
        - Most referrals (3.12 avg)
        - Highest current monthly charge ($89.97)
        - Strong service adoption: 97% phone service, 71% Streaming TV, 95% unlimited data
        - Highest share of two-year contracts (45.5%)

        **🎯 Retention Strategy:**  
        Reward this high-value segment with exclusive loyalty perks, early upgrades, VIP service options, and referral incentives.
        """)

    with st.expander("B - Balanced Bundle Seekers", expanded=False):
        st.markdown("""
        **Key Characteristics:**
        - Moderate tenure (37.07 months)
        - Solid balance across phone + internet + streaming
        - Fiber optic internet is popular (48%)
        - High extra data charges ($4.8), indicating heavy usage
        - Older age group (49.2 avg), tech-comfortable but cautious

        **🎯 Opportunity:**  
        Offer customized streaming & data bundles with loyalty rewards and value-added upgrades.
        """)

    with st.expander("C - Data-Capped Digitals", expanded=False):
        st.markdown("""
        **Key Characteristics:**
        - 100% have internet service, but 0% have unlimited data
        - Average revenue ($4,565) with moderate tenure (42.4 months)
        - Balanced contract types and low refund rate
        - High device protection & service adoption
        - Middle-aged demographic (48.5 avg)

        **🎯 Growth Strategy:**  
        Upsell unlimited data plans, content bundles, and exclusive streaming offers.
        """)

    with st.expander("D - Legacy Phone-Only Users", expanded=False):
        st.markdown("""
        **Key Characteristics:**
        - 100% have no internet service
        - Lowest average charges ($20.58/month)
        - Zero GB download & 0% online features
        - Highest share of mailed check payments (9.6%)
        - Mostly under contract (42% two-year), but low engagement

        **🎯 Conversion Strategy:**  
        Target with Internet bundles and digital education campaigns to boost ARPU.
        """)

    with st.expander("E - Churn-Risk New Users", expanded=False):
        st.markdown("""
        **Key Characteristics:**
        - Shortest tenure (16.28 months)
        - Lowest referrals (1.10 avg)
        - High churn profile: 78.5% month-to-month contracts
        - 75% have no premium support
        - Limited streaming & tech features
        - Heavy users of promotional offers (price-sensitive)

        **⚠️ Churn Risk: High**  
        **🎯 Retention Strategy:**  
        Target with contract lock-in incentives, personalized upgrade bundles, and retention-specific offers.
        """)



if __name__ == "__main__":
    show_persona_page()
