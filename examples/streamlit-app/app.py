"""Example Streamlit application for testing app-publisher."""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Example Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Example Streamlit Dashboard")
st.markdown("This is a sample Streamlit application deployed using app-publisher")

# Sidebar
st.sidebar.header("Configuration")
chart_type = st.sidebar.selectbox(
    "Select Chart Type",
    ["Line Chart", "Bar Chart", "Area Chart"]
)

num_points = st.sidebar.slider("Number of data points", 10, 100, 50)

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total Users",
        value="1,234",
        delta="12"
    )

with col2:
    st.metric(
        label="Revenue",
        value="$45,678",
        delta="-3%"
    )

with col3:
    st.metric(
        label="Active Sessions",
        value="456",
        delta="23"
    )

# Generate sample data
st.subheader("Sample Data Visualization")

data = pd.DataFrame({
    'Date': pd.date_range(start='2024-01-01', periods=num_points),
    'Value 1': np.random.randn(num_points).cumsum(),
    'Value 2': np.random.randn(num_points).cumsum(),
})

if chart_type == "Line Chart":
    st.line_chart(data.set_index('Date'))
elif chart_type == "Bar Chart":
    st.bar_chart(data.set_index('Date'))
else:
    st.area_chart(data.set_index('Date'))

# Data table
st.subheader("Raw Data")
st.dataframe(data, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
