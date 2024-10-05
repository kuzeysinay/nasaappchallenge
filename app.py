import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

# Load the dataset
df = pd.read_csv('solid-waste-disposal_emissions_sources.csv')

# Extract relevant columns: latitude, longitude, CO2 emissions, year, and gas type
df_filtered = df[['lat', 'lon', 'start_time', 'source_name', 'emissions_quantity', 'source_id', 'gas']]

# Filter for only 'co2e_100yr' gas type
df_filtered = df_filtered[df_filtered['gas'] == 'co2e_100yr']

# Calculate the number of unique disposal sites (unique source_ids)
total_sites = df_filtered['source_id'].nunique()

# Adding a year column for easier filtering
df_filtered['year'] = pd.to_datetime(df_filtered['start_time']).dt.year

# Sort by emissions_quantity to calculate ranks
df_filtered['rank'] = df_filtered['emissions_quantity'].rank(method="min", ascending=False).astype(int)

# Set min and max radius for circle sizes
min_radius = 2000  # Minimum size for circles
max_radius = 10000  # Maximum size for circles

# Apply log scale to emissions data and normalize between min_radius and max_radius
df_filtered['emission_scaled'] = np.interp(
    np.log1p(df_filtered['emissions_quantity']),  # Apply logarithmic scale
    (np.log1p(df_filtered['emissions_quantity'].min()), np.log1p(df_filtered['emissions_quantity'].max())),
    (min_radius, max_radius)
)

# Formatting emissions as a user-friendly string
df_filtered['emissions_formatted'] = df_filtered.apply(lambda row: f"{int(row['emissions_quantity']):,}", axis=1)

# Filtering for 2021 and 2022 data
df_2021 = df_filtered[df_filtered['year'] == 2021]
df_2022 = df_filtered[df_filtered['year'] == 2022]

# Streamlit UI
st.title("Landfill Emissions in Turkey (CO2e_100yr)")

# Switch (radio) to toggle between years
year = st.radio('Select Year', [2021, 2022])

# Choose data based on the selected year
if year == 2021:
    data_to_display = df_2021
else:
    data_to_display = df_2022

# Defining map view
view_state = pdk.ViewState(
    latitude=data_to_display['lat'].mean(),
    longitude=data_to_display['lon'].mean(),
    zoom=6
)

# Layer to display points with sizes based on CO2 emissions and new color
layer = pdk.Layer(
    'ScatterplotLayer',
    data=data_to_display,
    get_position='[lon, lat]',
    get_radius='emission_scaled',  # Map the radius between min and max values
    get_color=[170, 170, 70, 140],  # Nauseating yellow-green color with some transparency
    pickable=True
)

# Render map with emission info in the tooltip, displaying the formatted emissions and rank
r = pdk.Deck(
    layers=[layer], 
    initial_view_state=view_state, 
    tooltip={
        "html": """
        <div style="background-color: rgb(170, 170, 70); padding: 5px; border-radius: 5px; width: fit-content;">
            <b style="color: #fff">Disposal site</b>
        </div>
        <b style="color: #fff">{source_name}</b><br>
        <div style="font-size: 24px; font-weight: bold; color: #fff;">
            {emissions_formatted}t CO<sub>2</sub>e100 in {year}
        </div>
        <div style="font-size: 16px; color: grey;">
            {rank} out of """ + str(total_sites) + """ disposal sites
        </div>
        """,
        "style": {"color": "black"}
    }
)

st.pydeck_chart(r)
