import streamlit as st
import json
import folium
from streamlit_folium import folium_static
import plotly.express as px
import pandas as pd
from PIL import Image
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

# Set Streamlit page title and header
st.set_page_config(page_title='Renewable Energy Dashboard', layout="wide")

from PIL import Image
import base64
from io import BytesIO

# Local paths to your images
logo1_path = r"D:\UPNEDA_Dashboard\ceed logo.jpg"
logo2_path = r"C:\Users\sachi\Downloads\uttar-pradesh-government-logo-1FA161CB94-seeklogo.com.png"
logo3_path = r"C:\Users\sachi\Downloads\UPNEDA_logo.jpg"
# Open and resize the images
img1 = Image.open(logo1_path).resize((150, 130))
img2 = Image.open(logo2_path).resize((150, 150))
img3 = Image.open(logo3_path).resize((180, 150))



def display_header():

    # Apply CSS to center the title
    st.markdown(
        """
        <style>
        .centered-title {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    # Create three columns
    col1, col2, col3 = st.columns([1, 6, 1])

    with col1:
        st.image(img1, width=150)

    with col2:
        st.markdown('<div class="centered-title"><h1>Renewable Energy Dashboard</h1></div>', unsafe_allow_html=True)

    with col3:
        st.image(img3, width=150)

display_header()


# Function to load GeoJSON data - cached for performance

def load_geojson_data(file_path):
    with open(file_path) as f:
        return json.load(f)

geojson_data = load_geojson_data(r"D:\UPNEDA_Dashboard\UP_Dashboard_data.geojson")

# Function to load state data from a CSV file - cached for performance

def load_state_data(file_path):
    return pd.read_csv(file_path)

state_data = load_state_data(r"D:\UPNEDA_Dashboard\UP_Dashboard_data.csv")

# Dictionary to map column names to more user-friendly technology names
rooftop_technology_aliases = {
    "Combined Rooftop Capacity (kWp)": "Solar Rooftop Total (kWp)",  # New combined entry
    "R Capacity Installed (kW)": "Solar Rooftop Residential (kWp)",
    "NR Capacity Installed (kW)": "Solar Rooftop Non-Residential (kWp)"
}

# Add a selectbox for rooftop technology selection with an initial option
selected_rooftop_technology_alias = st.selectbox(
    "Select a rooftop category", 
    ["Select an option"] + list(rooftop_technology_aliases.values()), 
    key="rooftop_technology_select"
)

# Check if the user has selected a valid option
if selected_rooftop_technology_alias != "Select an option":
    # Get the actual column name for the selected rooftop technology
    selected_rooftop_technology = [key for key, value in rooftop_technology_aliases.items() if value == selected_rooftop_technology_alias][0]

    # Function to prepare data for the plot - cached for performance
    def prepare_plot_data(geojson_data, state_data, selected_rooftop_technology):
        plot_data = []
        for feature in geojson_data['features']:
            district = feature['properties']['Dist_Name']
            if selected_rooftop_technology == "Combined Rooftop Capacity (kWp)":
                value = (feature['properties'].get("R Capacity Installed (kW)", 0) +
                         feature['properties'].get("NR Capacity Installed (kW)", 0))
            else:
                value = feature['properties'].get(selected_rooftop_technology, 0)
            plot_data.append({"District": district, "Value": value})
        plot_data.sort(key=lambda x: x["Value"], reverse=True)
        return plot_data

    plot_data = prepare_plot_data(geojson_data, state_data, selected_rooftop_technology)

    # Create a horizontal bar plot using Plotly Express
    fig = px.bar(
        plot_data,
        x="Value",
        y="District",
        orientation='h',
        labels={"Value": selected_rooftop_technology_alias, "District": "District"},
        title=f'{selected_rooftop_technology_alias} across Uttar Pradesh'
    )
    fig.update_layout(
        width=400, 
        height=1250, 
        margin=dict(l=200),  # Adjust left margin for district names
        xaxis=dict(gridcolor='LightGrey'),  # Add grid lines for x-axis
        yaxis=dict(gridcolor='LightGrey', categoryorder='total ascending')  # Add grid lines for y-axis and sort categories
    )

    # Create a Folium map
    m = folium.Map(location=[26.5145, 80.55], zoom_start=6.5, min_zoom=5, max_zoom=15, tiles='Cartodb Positron', control_scale=True)

    # Add a choropleth layer to the map based on the selected rooftop technology
    if selected_rooftop_technology == "Combined Rooftop Capacity (kWp)":
        state_data['Combined Rooftop Capacity (kWp)'] = state_data["R Capacity Installed (kW)"] + state_data["NR Capacity Installed (kW)"]
        columns = ["Dist_Name", "Combined Rooftop Capacity (kWp)"]
    else:
        columns = ["Dist_Name", selected_rooftop_technology]

    folium.Choropleth(
        geo_data=geojson_data,
        data=state_data,
        columns=columns,
        key_on="feature.properties.Dist_Name",
        fill_color='YlGn',  # color scale (you can choose different color scales)
        fill_opacity=1.0,
        line_opacity=0.5,
        legend_name=selected_rooftop_technology_alias
    ).add_to(m)
    m.options['scrollWheelZoom'] = False

    # Layout adjustments for responsiveness
    col1, col2 = st.columns([1,1])  # Adjust column widths for responsiveness
    with col1:
        folium_static(m, width=800, height=900)   
    with col2:
        st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Please select a option.")


st.header("Solar Rooftop Systems on Goverment Buildings")

# Load the data
data = pd.read_csv(r"D:\UPNEDA_Dashboard\Geolocations.csv")


# Load GeoJSON data for Uttar Pradesh boundary
with open(r"D:\UPNEDA_Dashboard\UP_Data.geojson") as f:
    uttar_pradesh_geojson = json.load(f)

# Create a map centered around Uttar Pradesh, India
map_uttar_pradesh = folium.Map(location=[27.0, 80.0], zoom_start=7,tiles='cartodb dark_matter', control_scale=False)

# Add GeoJSON layer to the map
folium.GeoJson(uttar_pradesh_geojson, name="Uttar Pradesh Boundary").add_to(map_uttar_pradesh)

# Add markers to the map with custom tooltips
for _, row in data.iterrows():
    tooltip = f"District: {row['District']}<br>Capacity Installed: {row['Capacity Installed (kW)']} kW"
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        tooltip=tooltip
    ).add_to(map_uttar_pradesh)


map_uttar_pradesh.options['scrollWheelZoom'] = False
# Display the map
folium_static(map_uttar_pradesh, width=1600, height=800)