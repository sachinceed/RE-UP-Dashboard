import streamlit as st
import json
import folium
from streamlit_folium import folium_static
import plotly.express as px
import pandas as pd
from PIL import Image


# Set Streamlit page title and header
st.set_page_config(page_title='Renewable Energy Dashboard',layout="wide")



# Centering header using HTML and CSS
#st.markdown(
#    """
#    <div style="display: flex; justify-content: center;">
#        <h1 style="text-align: center;">Renewable Energy Dashboard for Uttar Pradesh</h1>
#    </div>
#    """,
#    unsafe_allow_html=True
#)


# Local paths to your images
logo1_path = "Streamlit_app/Logos/ceed logo2.png"
logo3_path = "Streamlit_app/Logos/Neda.png"
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
        st.markdown('<div class="centered-title"><h1>Renewable Energy Dashboard for Uttar Pradesh</h1></div>', unsafe_allow_html=True)

    with col3:
        st.image(img1, width=150)

display_header()

# Load GeoJSON data
with open("Streamlit_app/Data/UP_Data_New.geojson") as f:
    geojson_data = json.load(f)

# Extract district names for the dropdown menu and add "Uttar Pradesh" option
districts = ["All Districts"] + [feature['properties']['Dist_Name'] for feature in geojson_data['features']]
districts.sort()

# Add a selectbox for district selection with "Uttar Pradesh" as the default value
selected_district = st.selectbox("Select a district", districts, index=districts.index("All Districts"))

# Function to customize tooltip
def style_function(feature):
    if feature['properties']['Dist_Name'] == selected_district:
        return {
            'fillColor': '#ff7800',
            'color': 'Black',
            'weight': 3,
            'dashArray': '4, 4',
            'fillOpacity': 0.7,
        }
    else:
        return {
            'fillColor': '#10ef3b',
            'color': 'Black',
            'weight': 2,
            'dashArray': '4, 4',
            'fillOpacity': 0.7,
        }

# Create a Folium map
m = folium.Map(location=[26.5145, 80.55], zoom_start=7, min_zoom=5, max_zoom=15, tiles='cartodb dark_matter', control_scale=False)

# Add GeoJson data to the map
folium.GeoJson(
    geojson_data,
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=[
            'Dist_Name', "SP_cap(MW)", "Combined Rooftop Capacity (kW)",
            "DDG_Solar_Cap_KW", "Minigrid_cap_KW", "SSL_Count", "Biomass", "Floating solar(MW)", "Hydro power","Utility(MW)"
        ],
        aliases=[
            'District:', "Solar pump (hp)", "Solar Rooftop Capacity (kWp)",
            "Decentralised Distributed generation (kW)", "Mini Grid (kW)",
            "Solar street lights (Nos.)", "Biomass", "Floating solar (MW)", "Hydro Power (MW)","Utility solar"
        ]
    )
).add_to(m)

# Lock the zoom level
m.options['scrollWheelZoom'] = False

folium.LayerControl().add_to(m)

# Center the map using CSS styling
st.markdown(
    """
    <style>
    .map-container {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

left_co, cent_co,last_co = st.columns([1,10,6])
with cent_co:
    folium_static(m, width=1300, height=800)



def get_value_or_zero(properties, key):
    value = properties.get(key)
    if value is None:
        return 0
    try:
        # Try to convert the value to a float
        return float(value)
    except ValueError:
        # If conversion fails, return 0
        return 0

# Initialize aggregated data
aggregated_data = {
    "SP_cap(MW)": 0.0,
    "Combined Rooftop Capacity (kW)": 0.0,
    "DDG_Solar_Cap_KW": 0.0,
    "Minigrid_cap_KW": 0.0,
    "SSL_Count": 0,
    "Biomass": 0.0,
    "Floating solar(MW)": 0.0,
    "Hydro power": 0.0,
    "Utility(MW)": 0.0,
    "Utility_OA(MW)": 0.0
}

if selected_district == "All Districts":
    # Aggregate data for all districts
    for feature in geojson_data['features']:
        aggregated_data["SP_cap(MW)"] += get_value_or_zero(feature['properties'], "SP_cap(MW)")
        aggregated_data["Combined Rooftop Capacity (kW)"] += get_value_or_zero(feature['properties'], "Combined Rooftop Capacity (kW)")
        aggregated_data["DDG_Solar_Cap_KW"] += get_value_or_zero(feature['properties'], "DDG_Solar_Cap_KW")
        aggregated_data["Minigrid_cap_KW"] += get_value_or_zero(feature['properties'], "Minigrid_cap_KW")
        aggregated_data["SSL_Count"] += int(get_value_or_zero(feature['properties'], "SSL_Count"))
        aggregated_data["Biomass"] += get_value_or_zero(feature['properties'], "Biomass")
        aggregated_data["Floating solar(MW)"] += get_value_or_zero(feature['properties'], "Floating solar(MW)")
        aggregated_data["Hydro power"] += get_value_or_zero(feature['properties'], "Hydro power")
        aggregated_data["Utility(MW)"] += get_value_or_zero(feature['properties'], "Utility(MW)")
        aggregated_data["Utility_OA(MW)"] += get_value_or_zero(feature['properties'], "Utility_OA(MW)")
else:
    for feature in geojson_data['features']:
        if feature['properties']['Dist_Name'] == selected_district:
            aggregated_data["SP_cap(MW)"] = get_value_or_zero(feature['properties'], "SP_cap(MW)")
            aggregated_data["Combined Rooftop Capacity (kW)"] = get_value_or_zero(feature['properties'], "Combined Rooftop Capacity (kW)")
            aggregated_data["DDG_Solar_Cap_KW"] = get_value_or_zero(feature['properties'], "DDG_Solar_Cap_KW")
            aggregated_data["Minigrid_cap_KW"] = get_value_or_zero(feature['properties'], "Minigrid_cap_KW")
            aggregated_data["SSL_Count"] = int(get_value_or_zero(feature['properties'], "SSL_Count"))
            aggregated_data["Biomass"] = get_value_or_zero(feature['properties'], "Biomass")
            aggregated_data["Floating solar(MW)"] = get_value_or_zero(feature['properties'], "Floating solar(MW)")
            aggregated_data["Hydro power"] = get_value_or_zero(feature['properties'], "Hydro power")
            aggregated_data["Utility(MW)"] = get_value_or_zero(feature['properties'], "Utility(MW)")
            aggregated_data["Utility_OA(MW)"] = get_value_or_zero(feature['properties'], "Utility_OA(MW)")
            break

def format_value(value):
    if isinstance(value, (int, float)):
        return f"{value:,.2f}"
    return value

# Arrange the map and metrics side by side
col13, col14 = st.columns([1,1])

# Display the metrics and the pie chart
with col13:
    st.markdown(f"<h3 style='text-align: center; font-size: 30px;'>{selected_district}</h3>", unsafe_allow_html=True)
   
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    col7, col8, col9 = st.columns(3)
    col10, col11, col12 = st.columns(3)
   
    col1.metric("Utility Scale Solar (MW)", format_value(aggregated_data['Utility(MW)']))
    col2.metric("Solar Rooftop (kW)", format_value(aggregated_data['Combined Rooftop Capacity (kW)']))
    col3.metric("Decentralised Distributed Solar (kW)", format_value(aggregated_data['DDG_Solar_Cap_KW']))
    col4.metric("Mini Grid (kW)", format_value(aggregated_data['Minigrid_cap_KW']))
    col5.metric("Solar street lights (Nos.)", format_value(aggregated_data['SSL_Count']))
    col6.metric("Floating Solar (MW)", format_value(aggregated_data['Floating solar(MW)']))
    col7.metric("Biomass (TPD)", format_value(aggregated_data['Biomass']))
    col8.metric("Hydro Power (MW)", format_value(aggregated_data['Hydro power']))
    col9.metric("Solar Water Pump (hp)", format_value(aggregated_data['SP_cap(MW)']))

aggregated_data['SP_cap_kW'] = aggregated_data['SP_cap(MW)'] * 0.7457  # HP to kW
aggregated_data['Floating_solar_kW'] = aggregated_data['Floating solar(MW)'] * 1000  # MW to kW
aggregated_data['Utility_kW'] = (aggregated_data['Utility(MW)']) * 1000  # MW to kW

# Create the DataFrame with standardized units (kW)
pie_data = pd.DataFrame({
    'Category': ['Solar Rooftop Capacity (kW)', 'DDG Solar Capacity (kW)',
                 'Mini Grid Capacity (kW)', 'Floating Solar Capacity (kW)', 'Utility Scale Solar Capacity (kW)'],
    'Capacity': [aggregated_data['Combined Rooftop Capacity (kW)'],
                 aggregated_data['DDG_Solar_Cap_KW'], aggregated_data['Minigrid_cap_KW'],
                 aggregated_data['Floating_solar_kW'], aggregated_data['Utility_kW']]
})

# Define the color map
color_map = {
    'Solar Rooftop Capacity (kW)': 'yellow',
    'DDG Solar Capacity (kW)': 'brown',
    'Mini Grid Capacity (kW)': 'lightcoral',
    'Floating Solar Capacity (kW)': 'red',
    'Utility Scale Solar Capacity (kW)': 'orange'
}

pie_fig = px.pie(pie_data, values='Capacity', names='Category',
                 color='Category', color_discrete_map=color_map,
                 hole=0.7)

pie_fig.update_traces(hoverinfo='label+value', 
                      hovertemplate='%{label}<br> %{value} kW')


# Update layout for a professional look
pie_fig.update_layout(
    title_text='Share of Installed Solar Capacity',
    title_font=dict(size=30, color='white'),
    title_y=0.95,  # Adjust this value to increase/decrease the gap
    #legend_title_text='Category',
    legend=dict(
        x=1,
        y=0.5,
        traceorder='normal',
        font=dict(size=12),
        bgcolor='rgba(260, 255, 255, 0.5)',
        bordercolor='Black',
        borderwidth=1
    ),
    margin=dict(l=40, r=40, t=100, b=40),  # Increase the top margin to create more space
    hoverlabel=dict(
        bgcolor="black",
        font_size=16,
        font_family="Rockwell"
    )
)

with col14:
    #st.markdown(f"<h3 style='text-align: center; font-size: 30px;'>Solar Installation Distribution {selected_district}</h3>", unsafe_allow_html=True)
    st.plotly_chart(pie_fig, height=50, width=50)




####################################################################################Technology Selection Part###########################################################################################################################
# Function to load GeoJSON data
def load_geojson_data(file_path):
    with open(file_path) as f:
        return json.load(f)

geojson_data = load_geojson_data("Streamlit_app/Data/UP_Data_New.geojson")

# Function to load state data from a CSV file - cached for performance
def load_state_data(file_path):
    return pd.read_csv(file_path)

state_data = load_state_data("Streamlit_app/Data/UP_Dashboard - UP_Dashboard_plotting_Data.csv")

# Dictionary to map column names to more user-friendly technology names
technology_aliases = {
    "SP_cap(MW)": "Solar pump (hp)",
    "SP_Counts": "Solar pump counts",  # New technology
    "Combined Rooftop Capacity (kW)": "Solar Rooftop (kW)",  # New combined entry
    "DDG_Solar_Cap_KW": "Decentralised Distributed Generation (kW)",
    "DDG_Solar_Counts": "DDG Solar counts",  # New technology
    "Minigrid_cap_KW": "Mini Grid (kW)",
    "Minigrid_Counts": "Minigrid counts",  # New technology
    "SSL_Count": "Solar street lights count",
    "Biomass(TDP)": "Biomass (TPD)",
    "Biomass_counts": "Biomass counts",  # New technology
    "Floating solar(MW)": "Floating solar (MW)",
    "Hydro power": "Hydro Power (MW)",
    "Utility(MW)": "Utility Scale Solar (MW)",  # New technology
    "Utility_counts(MW)": "Utility Scale Solar counts"  # New technology
}

# Add a placeholder option at the beginning
options = ["Select a technology"] + list(technology_aliases.values())

# Create a unique key for the selectbox based on the selected technology
selected_technology_alias = st.selectbox(
    "Select a technology",
    options,
    index=0,  # Set the default selected index to "Select a technology"
    key="technology_select"
)

# Check if a technology is selected and get the actual column name for the selected technology
selected_technology = None
if selected_technology_alias != "Select a technology":
    selected_technology = [key for key, value in technology_aliases.items() if value == selected_technology_alias][0]

# Prepare state data to ensure it's numeric and handle NaN values
def prepare_state_data(state_data, selected_technology):
    # Ensure the selected technology column is numeric
    state_data[selected_technology] = pd.to_numeric(state_data[selected_technology], errors='coerce')
    # Replace NaN values with 0 (or you can choose to drop them)
    state_data[selected_technology].fillna(0, inplace=True)
    return state_data

# Apply the function to clean the data if a technology is selected
if selected_technology:
    state_data = prepare_state_data(state_data, selected_technology)

    # Prepare data for the plot
    def prepare_plot_data(geojson_data, state_data, selected_technology):
        plot_data = []
        for feature in geojson_data['features']:
            district = feature['properties']['Dist_Name']
            value = feature['properties'].get(selected_technology, 0)
            plot_data.append({"District": district, "Value": value})
        plot_data.sort(key=lambda x: x["Value"], reverse=True)
        return plot_data

    plot_data = prepare_plot_data(geojson_data, state_data, selected_technology)

    # Create a horizontal bar plot using Plotly Express
    fig = px.bar(
        plot_data,
        x="Value",
        y="District",
        orientation='h',
        labels={"Value": selected_technology_alias, "District": "District"},
        title=f'{selected_technology_alias} across Uttar Pradesh'
    )
    fig.update_layout(
        width=700,
        height=1250,
        margin=dict(l=200),  # Adjust left margin for district names
        xaxis=dict(gridcolor='LightGrey'),  # Add grid lines for x-axis
        yaxis=dict(gridcolor='LightGrey', categoryorder='total ascending')  # Add grid lines for y-axis and sort categories
    )

    # Define tooltip fields and aliases based on selected technology
    tooltip_fields = ["Dist_Name", selected_technology]
    tooltip_aliases = ["District:", selected_technology_alias]

    # Create a Folium map
    m = folium.Map(location=[26.5145, 80.55], zoom_start=6, min_zoom=5, max_zoom=15, tiles='Cartodb Positron', control_scale=True)

    # Add a choropleth layer to the map based on the selected technology
    columns = ["Dist_Name", selected_technology]

    # Add custom breaks and tooltips based on specific technology conditions
    if selected_technology == "Hydro power":
        custom_breaks = [0, 2, 5, 10, 15, 20, 25, 30, 50, 70, 400]
        threshold_scale = custom_breaks
    elif selected_technology == "Floating solar (MW)":
        custom_breaks = [0, 2, 5, 10, 15, 20, 25, 30, 50, 70, 400]
        threshold_scale = custom_breaks
    else:
        threshold_scale = None

    folium.Choropleth(
        geo_data=geojson_data,
        data=state_data,
        columns=columns,
        key_on="feature.properties.Dist_Name",
        fill_color='YlGn',  # color scale (you can choose different color scales)
        fill_opacity=1.0,
        line_opacity=0.1,
        legend_name=selected_technology_alias,
        threshold_scale=threshold_scale  # Use custom breaks if provided
    ).add_to(m)

    # Define and add tooltips
    tooltip1 = folium.GeoJsonTooltip(
        fields=tooltip_fields,
        aliases=tooltip_aliases,
        localize=True
    )

    folium.GeoJson(
        geojson_data,
        style_function=lambda x: {'fillColor': 'transparent', 'color': 'black', 'weight': 1},
        tooltip=tooltip1
    ).add_to(m)

    m.options['scrollWheelZoom'] = False

    # Layout adjustments for responsiveness
    col1, col2 = st.columns([1, 1])  # Adjust column widths for responsiveness
    with col1:
        folium_static(m, width=600, height=700)
    with col2:
        st.plotly_chart(fig, use_container_width=True)
else:
    st.header("Please select a technology to display the data.")
