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
from PIL import Image


# Set Streamlit page title and header
st.set_page_config(page_title='Renewable Energy Dashboard', layout="wide")


logo1_path = r"D:\UPNEDA_Dashboard\Logos\ceed logo2.png"
logo3_path = r"D:\UPNEDA_Dashboard\Logos\Neda.png"
# Open and resize the images
img1 = Image.open(logo1_path).resize((250, 150))
img3 = Image.open(logo3_path).resize((350, 180))

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
    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        st.image(img3, width=150)

    with col2:
        st.markdown('<div class="centered-title"><h1>Solar Rooftop Status for Uttar Pradesh</h1></div>', unsafe_allow_html=True)

    with col3:
        st.image(img1, width=150)

display_header()



# Function to load GeoJSON data - cached for performance
def load_geojson_data(file_path):
    with open(file_path) as f:
        return json.load(f)

geojson_data = load_geojson_data(r"D:\UPNEDA_Dashboard\Updated data latest\UP_Data_New.geojson")

# Function to load state data from a CSV file - cached for performance
def load_state_data(file_path):
    return pd.read_csv(file_path)

state_data = load_state_data(r"D:\UPNEDA_Dashboard\Updated data latest\UP_Dashboard - UP_Dashboard_plotting_Data.csv")

# Dictionary to map column names to more user-friendly technology names
rooftop_technology_aliases = {
    "Combined Rooftop Capacity (kW)": "Solar Rooftop (kWp)",  # Already combined value
    "R Capacity Installed (kW)": "Solar Rooftop (Residential Buildings) (kWp)",
    "C&I Capacity Installed (kW)": "Solar Rooftop (Commercial and Industrial Buildings) (kWp)",
    "Govt Capacity Installed (kW)": "Solar Rooftop (Government Buildings) (kWp)"
}

# Add a selectbox for rooftop technology selection with "Select an option" as the default
selected_rooftop_technology_alias = st.selectbox(
    "Select a rooftop category", 
    ["Select an option"] + list(rooftop_technology_aliases.values()), 
    index=0,  # Ensure "Select an option" is the default
    key="rooftop_technology_select"
)

# Check if the user has selected a valid option
if selected_rooftop_technology_alias != "Select an option":
    # Get the actual column name for the selected rooftop technology
    selected_rooftop_technology = [
        key for key, value in rooftop_technology_aliases.items() 
        if value == selected_rooftop_technology_alias
    ][0]

    # Ensure the data in the selected column is numeric and handle NaN values
    state_data[selected_rooftop_technology] = pd.to_numeric(
        state_data[selected_rooftop_technology], errors='coerce'
    )
    state_data[selected_rooftop_technology].fillna(0, inplace=True)  # Replace NaNs with 0

    # Function to prepare data for the plot
    def prepare_plot_data(geojson_data, state_data, selected_rooftop_technology):
        plot_data = []
        for feature in geojson_data['features']:
            district = feature['properties']['Dist_Name']
            value = feature['properties'].get(selected_rooftop_technology, 0)
            plot_data.append({"District": district, "Value": value})
        plot_data.sort(key=lambda x: x["Value"], reverse=True)
        return plot_data

    # Define the columns for the choropleth
    columns = ["Dist_Name", selected_rooftop_technology]

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
        width=700, 
        height=1250, 
        margin=dict(l=200),  # Adjust left margin for district names
        xaxis=dict(gridcolor='LightGrey'),  # Add grid lines for x-axis
        yaxis=dict(gridcolor='LightGrey', categoryorder='total ascending')  # Add grid lines for y-axis and sort categories
    )

    # Create a Folium map
    m = folium.Map(location=[26.5145, 80.55], zoom_start=6, min_zoom=5, max_zoom=15, tiles='Cartodb Positron', control_scale=True)

    # Add a choropleth layer without custom bins
    folium.Choropleth(
        geo_data=geojson_data,
        data=state_data,
        columns=columns,
        key_on="feature.properties.Dist_Name",
        fill_color='YlGn',  
        fill_opacity=1.0,
        line_opacity=0.5,
        legend_name=selected_rooftop_technology_alias
    ).add_to(m)

    # Conditionally add tooltip based on the selected technology
    tooltip1 = folium.GeoJsonTooltip(
        fields=["Dist_Name", selected_rooftop_technology],
        aliases=["District Name", selected_rooftop_technology_alias],
        localize=True
    )
    folium.GeoJson(
        geojson_data,
        style_function=lambda x: {'fillColor': 'transparent', 'color': 'black', 'weight': 1},
        tooltip=tooltip1
    ).add_to(m)

    m.options['scrollWheelZoom'] = True

    # Layout adjustments for responsiveness
    col1, col2 = st.columns([1, 1])  # Adjust column widths for responsiveness
    with col1:
        folium_static(m, width=600, height=700)   
    with col2:
        st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Please select an option.")


#################################################################################################################################################################################################################################################
st.header("Solar Rooftop Systems on Government Buildings")


def load_data(file_path):
    return pd.read_csv(file_path, encoding='ISO-8859-1')  # Specify encoding

def load_geojson(file_path):
    with open(file_path) as f:
        return json.load(f)

def valid_coordinates(lat, lon):
    return pd.notna(lat) and pd.notna(lon)

# Load data and GeoJSON
data_ongrid = load_data("D:/UPNEDA_Dashboard/geolocations for ongridand offgrid/Ongrid.csv")
data_offgrid = load_data("D:/UPNEDA_Dashboard/geolocations for ongridand offgrid/Offgrid.csv")
uttar_pradesh_geojson = load_geojson("D:/UPNEDA_Dashboard/UP_Data.geojson")

# Create maps
def create_map(data, geojson, map_center, zoom_start, tiles):
    map_obj = folium.Map(location=map_center, zoom_start=7, tiles=tiles, control_scale=False)
    folium.GeoJson(geojson, name="Uttar Pradesh Boundary").add_to(map_obj)
    for _, row in data.iterrows():
        if valid_coordinates(row['Latitude'], row['Longitude']):
            tooltip = f"District: {row['District']}<br>Building: {row['Building name']}<br>Capacity Installed: {row['Capacity Installed (kW)']} kW"
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                tooltip=tooltip
            ).add_to(map_obj)
    map_obj.options['scrollWheelZoom'] =  False
    return map_obj

map_uttar_pradesh_ongrid = create_map(data_ongrid, uttar_pradesh_geojson, [27.0, 80.0], 7, 'cartodb dark_matter')
map_uttar_pradesh_offgrid = create_map(data_offgrid, uttar_pradesh_geojson, [27.0, 80.0], 7, 'cartodb dark_matter')


st.header("Solar Rooftop (Ongrid)")
folium_static(map_uttar_pradesh_ongrid, width=1300, height=750)  # Adjusted width and height for better responsiveness

st.header("Solar Rooftop (Offgrid)")
folium_static(map_uttar_pradesh_offgrid, width=1300, height=750)