import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Non-Flow Process Calculator", layout="wide")
st.title("Non-Flow Process Calculator with CoolProp")

# Sidebar inputs
st.sidebar.header("Process Inputs")
process_type = st.sidebar.selectbox(
    "Select Process Type",
    ["constant_volume", "constant_pressure", "isothermal", "adiabatic", "polytropic"]
)
T0 = st.sidebar.number_input("Initial Temperature (K)", value=300.0)
V0 = st.sidebar.number_input("Initial Specific Volume (m³/kg)", value=1.0)
n_points = st.sidebar.slider("Number of Points", 5, 50, 20)

# Process descriptions
process_descriptions = {
    "constant_volume": "Volume is constant. Pressure changes with temperature.",
    "constant_pressure": "Pressure is constant. Volume changes with temperature.",
    "isothermal": "Temperature is constant. Pressure changes with volume.",
    "adiabatic": "No heat transfer. P V^γ = constant.",
    "polytropic": "Generalized process: P V^n = constant."
}
st.info(process_descriptions[process_type])

# Calculate button
if st.button("Calculate"):
    api_url = f"http://127.0.0.1:8000/process/{process_type}?T0={T0}&V0={V0}&n_points={n_points}"
    
    with st.spinner("Calculating points..."):
        try:
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data from backend: {e}")
            data = []

    if data:
        df = pd.DataFrame(data)
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("T-s Chart")
            fig1 = px.line(df, x="s", y="T", markers=True, title="T-s Chart")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("P-v Chart")
            fig2 = px.line(df, x="v", y="P", markers=True, title="P-v Chart")
            st.plotly_chart(fig2, use_container_width=True)

        # CSV download
        csv = df.to_csv(index=False)
        st.download_button("Download Points as CSV", csv, "process_points.csv")
