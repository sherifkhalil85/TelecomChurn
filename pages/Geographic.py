import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Color schemes
churn_color = {'Joined':'#2ca02c', 'Stayed':'#1f77b4', 'Churned':'#ff7f0e'}
churn_cat_color = {'Low':'#2ca02c', 'Medium':'#1f77b4', 'High':'#ff7f0e', 'Very High':'#d62728'}

# Page config
st.set_page_config(
    page_title="Geographic Churn Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    df = pd.read_csv('Data/telecom_customer_churn_clustered.csv')
    # Prepare churn map data (from your notebook)
    map_df = df.copy()
    map_df['Churn'] = map_df['Churn'].replace({2:0})  # Convert churn labels if needed
    return df, map_df

df, map_df = load_data()

# Title
st.title("🌍 Geographic Churn Analysis")
st.markdown("Analyzing churn patterns across locations")

# =============================================
# Filters (City/State)
# =============================================
with st.expander("Customize", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        selected_states = st.multiselect(
            "Select States",
            options=df['State'].unique(),
            default=df['State'].unique()
        )

    with col2:
        selected_cities = st.multiselect(
            "Select Cities",
            options=df['City'].unique(),
            default=df['City'].unique()
        )

# Apply filters
filtered_df = df[df['State'].isin(selected_states) & df['City'].isin(selected_cities)]
filtered_map_df = map_df[map_df['State'].isin(selected_states) & map_df['City'].isin(selected_cities)]

# =============================================
# Dashboard Tabs (Now with Map)
# =============================================
tab1, tab2, tab3 = st.tabs([ "🏙️ City Analysis", "🏛️ State Analysis","🗺️ Churn Heatmap"])



with tab1:  # Existing City Analysis
    # Group and calculate
    city_df = filtered_df.groupby('City')['Customer Status'].value_counts().unstack(fill_value=0)
    city_df['total'] = city_df.sum(axis=1)
    city_df['churn_rate'] = (city_df.get('Churned', 0) / city_df['total']).round(3)
    city_df['stayed_rate'] = (city_df.get('Stayed', 0) / city_df['total']).round(3)
    city_df['joined_rate'] = (city_df.get('Joined', 0) / city_df['total']).round(3)
    city_df = city_df.reset_index()

    # 🔘 View Selector
    st.subheader("Top 20 Cities - Select View Type")
    bar_view_mode = st.radio(
        "Choose chart view:",
        options=["Total View", "Status Breakdown View"],
        index=0
    )

    # 🏙️ Get top 20 cities by total
    top_20_df = city_df.sort_values("total", ascending=False).head(20)
    top_20_cities = top_20_df['City'].tolist()

    if bar_view_mode == "Total View":
        fig_bar = px.bar(
            top_20_df,
            x='City', y='total',
            text='total',
            color='total',
            color_continuous_scale='Blues',
            title="Top 20 Cities by Total Number of Customers"
        )
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)

    else:
        # 🟦 Stacked Bar: Status Breakdown
        # Melt the top 20 city data to long format
        status_df = top_20_df.melt(
            id_vars='City',
            value_vars=['Churned', 'Stayed', 'Joined'],
            var_name='Customer Status',
            value_name='count'
        )

        fig_status = px.bar(
            status_df,
            x='City',
            y='count',
            color='Customer Status',
            barmode='stack',
            title="Customer Status Composition per City (Top 20 by Total Customers)",color_discrete_map=churn_color,text='count',
        )
        fig_status.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_status, use_container_width=True)

    # 🎯 Scatter Chart for Customer Rate Analysis
    st.subheader("Top Cities by Selected Customer Rate")

    min_customers = st.slider("Minimum customers to show", 5, 100, 20, key="city_min")
    y_axis_option = st.selectbox(
        "Select rate to visualize:",
        options=['churn_rate', 'stayed_rate', 'joined_rate'],
        format_func=lambda x: x.replace('_', ' ').title(),
        key="rate_option"
    )

    high_risk_cities = city_df[city_df['total'] >= min_customers].sort_values(y_axis_option, ascending=False)

    fig = px.scatter(
        high_risk_cities.head(25),
        x='total', y=y_axis_option,
        color=y_axis_option,
        hover_name='City',
        size='total',

        title=f"Top Cities by {y_axis_option.replace('_', ' ').title()} (Min {min_customers} Customers)"
    )
    st.plotly_chart(fig, use_container_width=True)


    # Summary 
    st.subheader("📊 Statistics and Insights")
    with st.expander("1️⃣ City Distribution & Outlier Detection"):
        def flag_outliers(df, col_name):
            q1 = df[col_name].quantile(0.25)
            q3 = df[col_name].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            df['out_low'] = (df[col_name] < lower).astype(int)
            df['out_high'] = (df[col_name] > upper).astype(int)
            return df

        city_df = flag_outliers(city_df, col_name='total')

        total_cities = len(city_df)
        low_outliers = city_df['out_low'].sum()
        high_outliers = city_df['out_high'].sum()
        high_outlier_percent = (high_outliers / total_cities) * 100
        high_outlier_total = city_df[city_df['out_high'] == 1]['total'].sum()
        overall_total = city_df['total'].sum()
        high_outlier_share = high_outlier_total / overall_total

        st.markdown(f"""
        - 🔢 Total Cities: **{total_cities}**  
        - ⬇️ Low Outliers: **{low_outliers}**  
        - ⬆️ High Outliers: **{high_outliers}** (**{high_outlier_percent:.2f}%** of cities)  
        - 🧮 High-Outlier Customer Share: **{high_outlier_total:,}** customers (**{high_outlier_share:.2%}** of all)
        """)

        st.dataframe((city_df['total'].describe().to_frame()).T)    

    with st.expander("2️⃣ Churn Rate Summary"):
        # Already calculated earlier: churn_rate, joined_rate
        city_df['New_customers%'] = (city_df['Joined'] / city_df['total']).round(2)
        city_df['churn_category'] = pd.cut(
            city_df['churn_rate'], 
            bins=[0, 0.25, 0.5, 0.75, 1.0],
            labels=['Low', 'Medium', 'High', 'Very High'],
            include_lowest=True
        )

        summary_city = city_df.groupby('churn_category').agg(
            City_Count=('City', 'count'),
            Total_Customers=('total', 'sum'),
            churned_customers=('Churned', 'sum'),
            New_customers=('Joined', 'sum')
        ).reset_index()

        summary_city['% of Cities'] = (summary_city['City_Count'] / summary_city['City_Count'].sum() * 100).round(2)
        summary_city['% of Customers'] = (summary_city['Total_Customers'] / summary_city['Total_Customers'].sum() * 100).round(2)

        re_fullfil = city_df['Joined'].sum() / city_df['Churned'].sum()
        st.markdown(f"""
        ##### Churn Category Thresholds:
        - Low: 0% - 25%  
        - Medium: 25% - 50%  
        - High: 50% - 75%  
        - Very High: 75% - 100%

        🔁 **New Customers to Churn Ratio**: **{re_fullfil:.2f}**
        (_Lower than 1 may indicate market share risk_)
        """)
        st.dataframe(summary_city)




    with st.expander("3️⃣  Churn Categories by Customers & Cities"):
        fig_pie = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                                subplot_titles=['% of Customers', '% of Cities'])

        fig_pie.add_trace(go.Pie(
            labels=summary_city['churn_category'],
            values=summary_city['Total_Customers'],
            marker_colors=[churn_cat_color[c] for c in summary_city['churn_category']]
        ), 1, 1)

        fig_pie.add_trace(go.Pie(
            labels=summary_city['churn_category'],
            values=summary_city['City_Count'],
            marker_colors=[churn_cat_color[c] for c in summary_city['churn_category']]
        ), 1, 2)

        fig_pie.update_layout(title_text='City Churn Categories: Customers vs Cities', template='presentation')
        st.plotly_chart(fig_pie, use_container_width=True)










with tab2:  # State-Level Analysis (replica of City tab but for State)
    # Group and calculate
    state_df = filtered_df.groupby('State')['Customer Status'].value_counts().unstack(fill_value=0)
    state_df['total'] = state_df.sum(axis=1)
    state_df['churn_rate'] = (state_df.get('Churned', 0) / state_df['total']).round(3)
    state_df['stayed_rate'] = (state_df.get('Stayed', 0) / state_df['total']).round(3)
    state_df['joined_rate'] = (state_df.get('Joined', 0) / state_df['total']).round(3)
    state_df = state_df.reset_index()

    # 🔘 View Selector
    st.subheader("Top 20 States - Select View Type")
    bar_view_mode = st.radio(
        "Choose chart view:",
        options=["Total View", "Status Breakdown View"],
        index=0,
        key="state_bar_mode"
    )

    # 🏩️ Get top 20 states by total
    top_20_df = state_df.sort_values("total", ascending=False).head(20)

    if bar_view_mode == "Total View":
        fig_bar = px.bar(
            top_20_df,
            x='State', y='total',
            text='total',
            color='total',
            color_continuous_scale='Blues',
            title="Top 20 States by Total Number of Customers"
        )
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        status_df = top_20_df.melt(
            id_vars='State',
            value_vars=['Churned', 'Stayed', 'Joined'],
            var_name='Customer Status',
            value_name='count'
        )
        fig_status = px.bar(
            status_df,
            x='State', y='count',
            color='Customer Status',
            barmode='stack',
            title="Customer Status Composition per State (Top 20 by Total Customers)",
            color_discrete_map=churn_color,
            text='count'
        )
        fig_status.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_status, use_container_width=True)

    # 🎯 Scatter Chart for Customer Rate Analysis
    st.subheader("Top States by Selected Customer Rate")

    min_customers = st.slider("Minimum customers to show", 5, 100, 20, key="state_min")
    y_axis_option = st.selectbox(
        "Select rate to visualize:",
        options=['churn_rate', 'stayed_rate', 'joined_rate'],
        format_func=lambda x: x.replace('_', ' ').title(),
        key="state_rate_option"
    )

    high_risk_states = state_df[state_df['total'] >= min_customers].sort_values(y_axis_option, ascending=False)

    fig = px.scatter(
        high_risk_states.head(25),
        x='total', y=y_axis_option,
        color=y_axis_option,
        hover_name='State',
        size='total',
        title=f"Top States by {y_axis_option.replace('_', ' ').title()} (Min {min_customers} Customers)"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Summary
    st.subheader("📊 Statistics and Insights")
    with st.expander("1️⃣ State Distribution & Outlier Detection"):
        def flag_outliers(df, col_name):
            q1 = df[col_name].quantile(0.25)
            q3 = df[col_name].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            df['out_low'] = (df[col_name] < lower).astype(int)
            df['out_high'] = (df[col_name] > upper).astype(int)
            return df

        state_df = flag_outliers(state_df, col_name='total')

        total_states = len(state_df)
        low_outliers = state_df['out_low'].sum()
        high_outliers = state_df['out_high'].sum()
        high_outlier_percent = (high_outliers / total_states) * 100
        high_outlier_total = state_df[state_df['out_high'] == 1]['total'].sum()
        overall_total = state_df['total'].sum()
        high_outlier_share = high_outlier_total / overall_total

        st.markdown(f"""
        - 📏 Total States: **{total_states}**  
        - ⬇️ Low Outliers: **{low_outliers}**  
        - ⬆️ High Outliers: **{high_outliers}** (**{high_outlier_percent:.2f}%** of states)  
        - 📊 High-Outlier Customer Share: **{high_outlier_total:,}** customers (**{high_outlier_share:.2%}** of all)
        """)

        st.dataframe((state_df['total'].describe().to_frame()).T)

    with st.expander("2️⃣ Churn Rate Summary"):
        state_df['New_customers%'] = (state_df['Joined'] / state_df['total']).round(2)
        state_df['churn_category'] = pd.cut(
            state_df['churn_rate'], 
            bins=[0, 0.25, 0.5, 0.75, 1.0],
            labels=['Low', 'Medium', 'High', 'Very High'],
            include_lowest=True
        )

        summary_state = state_df.groupby('churn_category').agg(
            State_Count=('State', 'count'),
            Total_Customers=('total', 'sum'),
            churned_customers=('Churned', 'sum'),
            New_customers=('Joined', 'sum')
        ).reset_index()

        summary_state['% of States'] = (summary_state['State_Count'] / summary_state['State_Count'].sum() * 100).round(2)
        summary_state['% of Customers'] = (summary_state['Total_Customers'] / summary_state['Total_Customers'].sum() * 100).round(2)

        re_fullfil = state_df['Joined'].sum() / state_df['Churned'].sum()
        st.markdown(f"""
        ##### Churn Category Thresholds:
        - Low: 0% - 25%  
        - Medium: 25% - 50%  
        - High: 50% - 75%  
        - Very High: 75% - 100%

        🔁 **New Customers to Churn Ratio**: **{re_fullfil:.2f}**
        (_Lower than 1 may indicate market share risk_)
        """)
        st.dataframe(summary_state)

    with st.expander("3️⃣ Churn Categories by Customers & States"):
        fig_pie = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                                subplot_titles=['% of Customers', '% of States'])

        fig_pie.add_trace(go.Pie(
            labels=summary_state['churn_category'],
            values=summary_state['Total_Customers'],
            marker_colors=[churn_cat_color[c] for c in summary_state['churn_category']]
        ), 1, 1)

        fig_pie.add_trace(go.Pie(
            labels=summary_state['churn_category'],
            values=summary_state['State_Count'],
            marker_colors=[churn_cat_color[c] for c in summary_state['churn_category']]
        ), 1, 2)

        fig_pie.update_layout(title_text='State Churn Categories: Customers vs States', template='presentation')
        st.plotly_chart(fig_pie, use_container_width=True)












    with tab3:  # NEW MAP TAB
        st.subheader("Churn Density Heatmap")

        if 'Latitude' in filtered_map_df.columns and 'Longitude' in filtered_map_df.columns:
            fig = px.density_mapbox(
                filtered_map_df,
                lat='Latitude',
                lon='Longitude',
                z='Churn',
                radius=10,
                zoom=5,
                hover_name='City',
                hover_data=['State', 'Customer Status'],
                color_continuous_scale='rainbow',
                mapbox_style='open-street-map',
                title='Customer Churn Density'
            )
            fig.update_layout(
                autosize=True,
                height=900,
                margin=dict(l=0, r=0, b=0, t=40)
            )
            st.plotly_chart(fig, use_container_width=True)


        else:
            st.warning("Map unavailable - Latitude/Longitude data missing")

        # 📍 Treemap: City Distribution by Churn Category
        st.markdown("### 🌳 City Breakdown by Churn Category")

        # Ensure churn_category exists (recalculate if not already available in session)
        if 'churn_category' not in city_df.columns:
            city_df['churn_rate'] = (city_df['Churned'] / city_df['total']).round(3)
            city_df['churn_category'] = pd.cut(
                city_df['churn_rate'], 
                bins=[0, 0.25, 0.5, 0.75, 1.0],
                labels=['Low', 'Medium', 'High', 'Very High'],
                include_lowest=True
            )

        fig = px.treemap(
            city_df,
            path=['churn_category', 'City'],
            values='total',
            color='churn_category',
            color_discrete_map=churn_cat_color,
            title='🗂️ Cities Grouped by Churn Category',
            template='presentation'
        )
        fig.update_layout(margin=dict(t=40, l=0, r=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
