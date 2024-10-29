import pandas as pd
import folium
import geopandas as gpd
from shapely.geometry import Point, LineString

# Load GTFS Data
def load_gtfs_data(folder_path):
    """Loads GTFS data files as DataFrames."""
    stops = pd.read_csv(f"{folder_path}/stops.txt")
    routes = pd.read_csv(f"{folder_path}/routes.txt")
    shapes = pd.read_csv(f"{folder_path}/shapes.txt")
    return stops, routes, shapes

# Map route names to colors
def get_route_color(route_long_name, route_color=None):
    """Returns a color based on the route name or route color field."""
    colors = {
        'RED': 'red',
        'GREEN': 'green',
        'BLUE': 'blue',
        'YELLOW': 'yellow',
        'MAGENTA': 'magenta',
        'VIOLET': 'purple',
        'AQUA': 'cyan',
        'ORANGE': 'orange',
        'GRAY': 'gray',
        'PINK': 'pink'
    }
    # Check if route_color field is available
    if route_color and not pd.isna(route_color):
        return f"#{route_color}"  # Convert route_color to hex if it exists
    # Fallback to route_long_name-based color
    for keyword, color in colors.items():
        if keyword in route_long_name.upper():
            return color
    return 'black'  # Default color if no keyword is found

# Create Folium Map with Stops and Routes in Colors
def create_folium_map(stops, routes, shapes):
    """Creates a folium map with GTFS stops and routes in specific colors."""
    # Center map around mean latitude and longitude
    center_lat, center_lon = stops['stop_lat'].mean(), stops['stop_lon'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

    # Add stops to the map with station names in popups
    for _, stop in stops.iterrows():
        folium.Marker(
            location=[stop['stop_lat'], stop['stop_lon']],
            popup=f"<strong>{stop['stop_name']}</strong>",  # Bold station names
            tooltip=stop['stop_name']  # Show station name on hover
        ).add_to(m)

    # Add routes to the map using shape points and route colors
    for shape_id, shape_points in shapes.groupby('shape_id'):
        # Find corresponding route using route_id
        route = routes[routes['route_id'] == shape_id]
        if not route.empty:
            route_long_name = route.iloc[0]['route_long_name']
            route_color_code = route.iloc[0].get('route_color', None)
            route_color = get_route_color(route_long_name, route_color_code)
        else:
            route_color = 'black'  # Default color if route_id is not found

        # Add the route as a PolyLine with the selected color
        points = shape_points[['shape_pt_lat', 'shape_pt_lon']].values.tolist()
        folium.PolyLine(points, color=route_color, weight=2.5, opacity=0.7).add_to(m)

    return m

# Main function
def main(folder_path):
    stops, routes, shapes = load_gtfs_data(folder_path)

    # Create and save the interactive map
    folium_map = create_folium_map(stops, routes, shapes)
    folium_map.save("gtfs_map.html")
    print("Interactive GTFS map saved as gtfs_map.html.")

# Run the script
if __name__ == "__main__":
    folder_path = "./DMRC_GTFS"  # Update with your GTFS data folder path
    main(folder_path)
