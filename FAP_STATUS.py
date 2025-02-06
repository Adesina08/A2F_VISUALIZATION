import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json

# Page configuration
st.set_page_config(layout="wide", page_title="A2F VISUALIZATION", page_icon="🌍")

# Display browser zoom recommendation 
st.markdown(
    """
    <div style="background-color: #e6f3ff; padding: 20px; border-radius: 10px; border: 2px solid #99ccff; margin: 20px 0; text-align: center;">
        <h3 style="color: #004080;">🌐 For the best experience, please set your browser zoom level to 75%.</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# Image to the sidebar
st.sidebar.image("OIP.jpg",  use_container_width=True)
st.sidebar.header("FAP VISUALIZATION")

# Function to load data
def load_data():
    return pd.read_csv("A2F_FAP_v1.csv")
    
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

# Function to load GeoJSON data for state boundaries
def load_state_geojson(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Function to load GeoJSON data for polygons based on selected state
def load_polygon_geojson_selected_state(selected_state):
    file_path = f"polygons/{selected_state.upper()}.geojson"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Function to generate map for FAP functionalities
def generate_map_fap_functionalities(selected_state, selected_fap_functionality, data, state_gdf, state_geojson_data):
    zoom_level = 5.85  # Adjusted zoom level for Nigeria
    center_lat = 9.0820  # Center of Nigeria latitude
    center_lon = 8.6753  # Center of Nigeria longitude
    
    # Load polygon GeoJSON data for the selected state
    if selected_state != 'All':
        polygon_geojson_data = load_polygon_geojson_selected_state(selected_state)
    else:
        polygon_geojson_data = None

    if selected_state != 'All':
        filtered_data = data[(data['STATE'] == selected_state) & ((data['FAP_FUNCTIONALITY'] == selected_fap_functionality) | (selected_fap_functionality == 'All'))]
        map_title = f"FAP FUNCTIONALITIES VISUALIZATION FOR {selected_state} - {selected_fap_functionality}"
        selected_state_gdf = state_gdf[state_gdf['admin1Name'] == selected_state]
        if not selected_state_gdf.empty:
            center_lat = selected_state_gdf.centroid.y.values[0]
            center_lon = selected_state_gdf.centroid.x.values[0]
            zoom_level = 7
    else:
        filtered_data = data[(data['FAP_FUNCTIONALITY'] == 'Active') | (data['FAP_FUNCTIONALITY'] == 'Inactive')]
        map_title = f"FAP FUNCTIONALITIES VISUALIZATION FOR NIGERIA - {selected_fap_functionality}"
        center_lat = 9.0820  # Center of Nigeria latitude
        center_lon = 8.6753  # Center of Nigeria longitude
        zoom_level = 5.85  # Adjusted zoom level

    # Defined colors for FAP functionalities
    fap_colors = {'Active': 'green', 'Inactive': 'red'}

    # Choropleth map for state boundaries
    fig = px.choropleth_mapbox(selected_state_gdf if selected_state != 'All' else state_gdf, 
                               geojson=state_gdf.geometry,  # Using GeoJSON data directly
                               locations=selected_state_gdf.index if selected_state != 'All' else state_gdf.index,  # Using index as locations
                               mapbox_style="carto-positron",
                               zoom=zoom_level,
                               opacity=0.5,
                               center={"lat": center_lat, "lon": center_lon}  # Setting center of map
                              )

    # Scatter plot for filtered data
    for fap_func, color in fap_colors.items():
        if selected_fap_functionality == 'All' or fap_func == selected_fap_functionality:
            fap_filtered_data = filtered_data[filtered_data['FAP_FUNCTIONALITY'] == fap_func]
            fig.add_trace(go.Scattermapbox(
                lat=fap_filtered_data["LATITUDE"],
                lon=fap_filtered_data["LONGITUDE"],
                mode="markers",
                marker=dict(
                    size=13,
                    color=color,
                    opacity=0.7,
                ),
                hovertext=fap_filtered_data['FAP_TYPE'] + ', ' + fap_filtered_data['FORMALITY'] + ', ' + fap_filtered_data['FAP_FUNCTIONALITY'],
                name=f"{fap_func}"  # Legend label for each marker
            ))

    # Polygons(EAs) to the figure/map
    if polygon_geojson_data:
        for feature in polygon_geojson_data["features"]:
            if feature["geometry"]["type"] == "Polygon":
                coords = feature["geometry"]["coordinates"][0]  # Extract the coordinates of the first polygon
                lats = [coord[1] for coord in coords]  #To  Extract latitude values
                lons = [coord[0] for coord in coords]  #To Extract longitude values
                fig.add_trace(go.Scattermapbox(
                    mode="lines",
                    lat=lats,
                    lon=lons,
                    line=dict(color="purple", width=4),
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

# Function to generate map for FAP types
def generate_map_fap_types(selected_state, selected_fap_type, data, state_gdf, state_geojson_data):
    zoom_level = 5.85  # Adjusted zoom level for Nigeria
    center_lat = 9.0820  # Center of Nigeria latitude
    center_lon = 8.6753  # Center of Nigeria longitude
    
    # Load polygon GeoJSON data for the selected state
    if selected_state != 'All':
        polygon_geojson_data = load_polygon_geojson_selected_state(selected_state)
    else:
        polygon_geojson_data = None

    if selected_state != 'All':
        filtered_data = data[data['STATE'] == selected_state]
        map_title = f"FAP TYPES VISUALIZATION FOR {selected_state}"
        selected_state_gdf = state_gdf[state_gdf['admin1Name'] == selected_state]
        if not selected_state_gdf.empty:
            center_lat = selected_state_gdf.centroid.y.values[0]
            center_lon = selected_state_gdf.centroid.x.values[0]
            zoom_level = 7
    else:
        filtered_data = data
        map_title = f"FAP TYPES VISUALIZATION FOR NIGERIA"
        center_lat = 9.0820  # Center of Nigeria latitude
        center_lon = 8.6753  # Center of Nigeria longitude
        zoom_level = 5.85  # Adjusted zoom level

    # Define colors for FAP types
    fap_colors = {
        'Financial Service agent (POS agents)': 'green',
        'Cooperative/ Social group/Women group/savings group/farmer groups etc.': 'blue',
        'MFI/MFB': 'red',
        'ATM (This does not include ATMs at a bank branch)': 'orange',
        'Bank branch': 'purple',
        'Payment services banks (MTN Y’ello, Money master, 9PSB, Hope)': 'yellow',
        'Moneylender': 'cyan',
        'Bureau De Change (BDC)': 'magenta',
        'Capital market operators (portfolio/fund managers)': 'lime',
        'Insurance company/agent/broker': 'brown',
        'Pension provider': 'teal',
        'Non-Interest Banks': 'pink',
        'Others (specify)': 'gray'
    }

    # Create choropleth map for state boundaries
    fig = px.choropleth_mapbox(selected_state_gdf if selected_state != 'All' else state_gdf, 
                               geojson=state_gdf.geometry,  # Use GeoJSON data directly
                               locations=selected_state_gdf.index if selected_state != 'All' else state_gdf.index,  # Use index as locations
                               mapbox_style="carto-positron",
                               zoom=zoom_level,
                               opacity=0.5,
                               center={"lat": center_lat, "lon": center_lon}  # Set center of map
                              )

    # Filter data based on selected FAP type
    if selected_fap_type != 'All':
        filtered_data = filtered_data[filtered_data['FAP_TYPE'] == selected_fap_type]

    # Add scatter plot for filtered data
    for fap_type, color in fap_colors.items():
        fap_filtered_data = filtered_data[filtered_data['FAP_TYPE'] == fap_type]
        fig.add_trace(go.Scattermapbox(
            lat=fap_filtered_data["LATITUDE"],
            lon=fap_filtered_data["LONGITUDE"],
            mode="markers",
            marker=dict(
                size=13,
                color=color,
                opacity=0.7,
            ),
            hovertext=fap_filtered_data['FAP_TYPE'] + ', ' + fap_filtered_data['FORMALITY'] + ', ' + fap_filtered_data['FAP_FUNCTIONALITY'],
            name=f"{fap_type}"  # Legend label for each marker
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
                    line=dict(color="purple", width=4),
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
            title="FAP Type"
        )
    )

    return fig

# Function to calculate average proximity for each EA
def calculate_average_proximity(selected_state_data, selected_fap_type):
    # Filter data by selected FAP type
    filtered_data = selected_state_data[selected_state_data['FAP_TYPE'] == selected_fap_type]
    
    # Group by EA and calculate average proximity for each EA
    avg_proximity_per_ea = filtered_data.groupby('EA NAME')['KM Diff Calculation'].mean().reset_index()
    
    return avg_proximity_per_ea

def generate_km_diff_heatmap(state_gdf, state_geojson_data, data, selected_fap_type, selected_state=None):
    # Center of Nigeria latitude and longitude
    center_lat = 9.0820
    center_lon = 8.6753
    
    # Adjusted zoom level
    zoom_level = 5.85

    title = f"Heatmap of average proximity to FAP in KM"

    if selected_state:
        # Filter data by selected state
        filtered_data = data[(data['FAP_TYPE'] == selected_fap_type) & (data['STATE'] == selected_state)]
        
        # Group data by state and calculate average KM Diff for the selected state
        avg_km_diff_by_state = filtered_data.groupby('STATE')['KM Diff Calculation'].mean().reset_index()
        
        # Merge average data with state GeoDataFrame for the selected state
        merged_data = state_gdf.merge(avg_km_diff_by_state, how='left', left_on='admin1Name', right_on='STATE')
        
        # Fill missing values with 0 for the selected state
        merged_data['KM Diff Calculation'].fillna(0, inplace=True)
        
        # Create choropleth map for the selected state only
        fig = px.choropleth_mapbox(merged_data, 
                                   geojson=merged_data.geometry,  # Use GeoDataFrame geometry
                                   locations=merged_data.index,  # Use index as locations
                                   color='KM Diff Calculation',  # Color by average Km_Diff_Calculation
                                   color_continuous_scale="greens",  # Choose color scale
                                   range_color=(0, merged_data['KM Diff Calculation'].max()),  # Set color range
                                   mapbox_style="carto-positron",
                                   zoom=zoom_level,
                                   opacity=0.5,
                                   center={"lat": center_lat, "lon": center_lon}  # Set center of map
                                  )
    else:
        # Filter data by selected FAP type
        filtered_data = data[data['FAP_TYPE'] == selected_fap_type]
        
        # Group data by state and calculate average KM Diff for each state
        avg_km_diff_by_state = filtered_data.groupby('STATE')['KM Diff Calculation'].mean().reset_index()
        
        # Merge average data with state GeoDataFrame
        merged_data = state_gdf.merge(avg_km_diff_by_state, how='left', left_on='admin1Name', right_on='STATE')
        
        # Fill missing values with 0
        merged_data['KM Diff Calculation'].fillna(0, inplace=True)
        
        # Create choropleth map for all states
        fig = px.choropleth_mapbox(merged_data, 
                                   geojson=merged_data.geometry,  # Use GeoDataFrame geometry
                                   locations=merged_data.index,  # Use index as locations
                                   color='KM Diff Calculation',  # Color by average Km_Diff_Calculation
                                   color_continuous_scale="greens",  # Choose color scale
                                   range_color=(0, merged_data['KM Diff Calculation'].max()),  # Set color range
                                   mapbox_style="carto-positron",
                                   zoom=zoom_level,
                                   opacity=0.5,
                                   center={"lat": center_lat, "lon": center_lon}  # Set center of map
                                  )

    # Calculate Center Coordinates of States
    center_pos = {}
    for feature in state_geojson_data["features"]:
        state_name = feature["properties"]["admin1Name"]
        centroid = state_gdf[state_gdf["admin1Name"] == state_name].geometry.centroid.iloc[0]
        center_pos[state_name] = [centroid.x, centroid.y]

    # Adding Text to the Map
    for state_name, coords in center_pos.items():
        avg_value = merged_data[merged_data["admin1Name"] == state_name]["KM Diff Calculation"].iloc[0]
        fig.add_trace(go.Scattermapbox(
            lat=[coords[1]],
            lon=[coords[0]],
            mode="text",
            textfont=dict(color="black", size=15),
            text=str(round(avg_value, 2)),
            showlegend=False
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
        title=title
    )

    return fig

# Define page 1 content
def page1():
    st.sidebar.header("FAP STATUS VISUALIZATION")
    st.title("FAP STATUS VISUALIZATION")

    # Define the file path
    file_path = "A2F_FAP_v1.csv"
    data = load_data(file_path)

    # Load GeoJSON data for state boundaries
    state_geojson_data = load_state_geojson("ngaadmbndaadm1osgof20161215.geojson")

    # Convert GeoJSON data to GeoDataFrame for state boundaries
    state_gdf = gpd.GeoDataFrame.from_features(state_geojson_data["features"])

    # Filter by state and FAP functionality
    states = ['All'] + sorted(list(data['STATE'].unique()))
    selected_state = st.sidebar.selectbox("Select State", states)

    fap_functionalities = ['All', 'Active', 'Inactive']
    selected_fap_functionality = st.sidebar.radio("Select FAP Functionality", fap_functionalities)

    # Display map in column 2
    col1, col2 = st.columns([10, 2], gap='medium')
    
    # Display the map
    with st.spinner("Loading Map..."):
        fig = generate_map_fap_functionalities(selected_state, selected_fap_functionality, data, state_gdf, state_geojson_data)
        col1.plotly_chart(fig, use_container_width=True)

    # Display counts in DataFrame
    col2.write(f"FAP Status Count - State Level")
    if selected_state != 'All':
        filtered_data = data[(data['STATE'] == selected_state) & ((data['FAP_FUNCTIONALITY'] == selected_fap_functionality) | (selected_fap_functionality == 'All'))]
        counts_by_state = filtered_data.groupby('STATE')['FAP_FUNCTIONALITY'].value_counts().unstack(fill_value=0)
        col2.table(counts_by_state)
    else:
        counts_by_state = data.groupby('STATE')['FAP_FUNCTIONALITY'].value_counts().unstack(fill_value=0)
        col2.table(counts_by_state)


# Define page 2 content
def page2():
    st.sidebar.header("FAP TYPE VISUALIZATION")
    st.title("FAP TYPE VISUALIZATION")
    
    # Define the file path
    file_path = "A2F_FAP_v1.csv"

    # Load data
    data = load_data(file_path)

    # Load GeoJSON data for state boundaries
    state_geojson_data = load_state_geojson("ngaadmbndaadm1osgof20161215.geojson")

    # Convert GeoJSON data to GeoDataFrame for state boundaries
    state_gdf = gpd.GeoDataFrame.from_features(state_geojson_data["features"])

    # Filter by state (if required)
    states = ['All'] + sorted(list(data['STATE'].unique()))
    selected_state = st.sidebar.selectbox("Select State", states)

    # Filter by FAP type
    fap_types = ['All'] + list(data['FAP_TYPE'].unique())
    selected_fap_type = st.sidebar.selectbox("Select FAP Type", fap_types)

    # Display the map
    with st.spinner("Loading Map..."):
        fig = generate_map_fap_types(selected_state, selected_fap_type, data, state_gdf, state_geojson_data)
        st.plotly_chart(fig, use_container_width=True)



# Define page 3 content
def page3():
 # Load GeoJSON data for state boundaries
    state_geojson_data = load_state_geojson("ngaadmbndaadm1osgof20161215.geojson")

    # Convert GeoJSON data to GeoDataFrame for state boundaries
    state_gdf = gpd.GeoDataFrame.from_features(state_geojson_data["features"])

    # Load data
    file_path = "A2F_FAP_v1.csv"  # Replace with your actual dataset file path
    data = load_data(file_path)

    # Get unique FAP types
    fap_types = data['FAP_TYPE'].unique().tolist()
    selected_fap_type = st.sidebar.selectbox("Select FAP Type", fap_types)

    # Get unique states
    states = data['STATE'].unique().tolist()
    states.insert(0, "All")
    selected_state = st.sidebar.selectbox("Select State", states)

    # Display the heatmap
    if selected_state == "All":
        fig = generate_km_diff_heatmap(state_gdf, state_geojson_data, data, selected_fap_type)
        st.plotly_chart(fig, use_container_width=True)
    else:
        col1, col2 = st.columns([9, 3])
        with col1:
            with st.spinner("Loading Average KM Diff Heatmap..."):
                fig = generate_km_diff_heatmap(state_gdf, state_geojson_data, data, selected_fap_type, selected_state)
                st.plotly_chart(fig, use_container_width=True)

        # Filter data for selected state
        selected_state_data = data[data['STATE'] == selected_state]
        
        # Calculate Average Proximity for each EA in the selected state and FAP type
        avg_proximity_per_ea = calculate_average_proximity(selected_state_data, selected_fap_type)
        
        # Display unique EAs and their calculated average proximity
        with col2:
            st.markdown(f"### FAP Proximity by EA in {selected_state} state")
            st.table(avg_proximity_per_ea)

# Render selected page based on selection in the sidebar
selected_page = st.sidebar.radio("Select Page", ["FAP Status Visualization", "FAP Type Visualization", "FAP Proximity Visualization"])

if selected_page == "FAP Status Visualization":
    page1()
elif selected_page == "FAP Type Visualization":
    page2()
elif selected_page == "FAP Proximity Visualization":
    page3()
