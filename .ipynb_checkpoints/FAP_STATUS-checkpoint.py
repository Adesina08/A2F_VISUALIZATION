import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json

st.set_page_config(layout="wide")

# Add image to the sidebar
st.sidebar.image("OIP.jpg", use_column_width=True)
st.sidebar.header("FAP STATUS VISUALIZATION")
st.title("FAP STATUS VISUALIZATION")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("A2F_FAP_v1.csv")

# Function to load GeoJSON data for state boundaries
def load_state_geojson(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Function to load GeoJSON data for polygons based on selected state
def load_polygon_geojson_selected_state(selected_state):
    file_path = f"polygons\{selected_state.upper()}.geojson"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_map(selected_state, fap_functionality, data, state_gdf, state_geojson_data):
    # Load polygon GeoJSON data for the selected state
    if selected_state != 'All':
        polygon_geojson_data = load_polygon_geojson_selected_state(selected_state)
    else:
        polygon_geojson_data = None

    if selected_state != 'All':
        filtered_data = data[(data['STATE'] == selected_state) & ((data['FAP_FUNCTIONALITY'] == fap_functionality) | (fap_functionality == 'All'))]
        map_title = f"FAP STATUS VISUALIZATION FOR {selected_state} - {fap_functionality}"
        selected_state_gdf = state_gdf[state_gdf['admin1Name'] == selected_state]
        if not selected_state_gdf.empty:
            center_lat = selected_state_gdf.centroid.y.values[0]
            center_lon = selected_state_gdf.centroid.x.values[0]
            zoom_level = 7
        else:
            st.warning("Selected state not found in GeoDataFrame. Defaulting to Nigeria view.")
            center_lat = 9.0820  # Center of Nigeria latitude
            center_lon = 8.6753  # Center of Nigeria longitude
            zoom_level = 5.5  # Adjusted zoom level
    else:
        filtered_data = data[(data['FAP_FUNCTIONALITY'] == 'Active') | (data['FAP_FUNCTIONALITY'] == 'Inactive')]
        map_title = f"FAP STATUS VISUALIZATION FOR NIGERIA - {fap_functionality}"
        center_lat = 9.0820  # Center of Nigeria latitude
        center_lon = 8.6753  # Center of Nigeria longitude
        zoom_level = 5.85  # Adjusted zoom level

    # Define colors for FAP functionalities
    fap_colors = {'Active': 'green', 'Inactive': 'red'}

    # Create choropleth map for state boundaries
    fig = px.choropleth_mapbox(selected_state_gdf if selected_state != 'All' else state_gdf, 
                               geojson=state_gdf.geometry,  # Use GeoJSON data directly
                               locations=selected_state_gdf.index if selected_state != 'All' else state_gdf.index,  # Use index as locations
                               mapbox_style="carto-positron",
                               zoom=zoom_level,
                               opacity=0.5,
                               center={"lat": center_lat, "lon": center_lon}  # Set center of map
                              )

    # Add scatter plot for filtered data
    for fap_func, color in fap_colors.items():
        if fap_functionality == 'All' or fap_func == fap_functionality:
            fap_filtered_data = filtered_data[filtered_data['FAP_FUNCTIONALITY'] == fap_func]
            fig.add_trace(go.Scattermapbox(
                lat=fap_filtered_data["LATITUDE"],
                lon=fap_filtered_data["LONGITUDE"],
                mode="markers",
                marker=dict(
                    size=15,
                    color=color,
                    opacity=0.7,
                ),
                hovertext=fap_filtered_data['FAP_TYPE'] + ', ' + fap_filtered_data['FORMALITY'] + ', ' + fap_filtered_data['FAP_FUNCTIONALITY'],
                name=f"{fap_func}"  # Legend label for each marker
            ))

    # Add polygons to the figure
    if polygon_geojson_data:
        for feature in polygon_geojson_data["features"]:
            if feature["geometry"]["type"] == "Polygon":
                coords = feature["geometry"]["coordinates"][0]  # Extract the coordinates of the first polygon
                lats = [coord[1] for coord in coords]  # Extract latitude values
                lons = [coord[0] for coord in coords]  # Extract longitude values
                fig.add_trace(go.Scattermapbox(
                    mode="lines",
                    lat=lats,
                    lon=lons,
                    line=dict(color="purple", width=1),
                    fill="toself",  # Fill the inside of the polygon
                    showlegend=False  # Exclude from legend
                ))

    # Set layout for the map
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom_level,
        ),
        height=850,
        margin=dict(r=0, l=0, t=50, b=0),
        title=map_title,
        legend=dict(
            title="FAP Functionality"
        )
    )

    return fig


def page1():
    data = load_data()

    # Load GeoJSON data for state boundaries
    state_geojson_data = load_state_geojson("ngaadmbndaadm1osgof20161215.geojson")

    # Convert GeoJSON data to GeoDataFrame for state boundaries
    state_gdf = gpd.GeoDataFrame.from_features(state_geojson_data["features"])

    # Filter by state and FAP functionality
    states = ['All'] + list(data['STATE'].unique())
    selected_state = st.sidebar.selectbox("Select State", states)

    fap_functionality = st.sidebar.radio("Select FAP Functionality", ['All', 'Active', 'Inactive'])

    # Display map in column 2
    col1, col2 = st.columns([10, 2], gap='medium')
    
    # Display the map
    with st.spinner("Loading Map..."):
        fig = generate_map(selected_state, fap_functionality, data, state_gdf, state_geojson_data)
        col1.plotly_chart(fig, use_container_width=True)

    # Display counts in DataFrame
    col2.write("FAP Status Count by State")
    counts_by_state = data.groupby('STATE')['FAP_FUNCTIONALITY'].value_counts().unstack(fill_value=0)
    col2.table(counts_by_state)

# Render selected page
page1()
