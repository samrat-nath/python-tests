## Importing Libraries
import pandas as pd
import geopandas as gpd
import folium
from pyproj import CRS
from shapely.geometry import Point
from geopy.distance import geodesic

# ============================================================
## Function Definiitons ##

#create_point - combines lat/long to a single point
#Function to create a point based on the latitude and longitude columns in a dataframe. Returns original dataframe with point geometry as a column
def create_point (df, Long, Lat):
    crs = CRS("epsg:4326")
    geometry = [Point(xy) for xy in zip(df[Long], df[Lat])]
    df = gpd.GeoDataFrame(df, geometry=geometry).set_crs(crs, allow_override=True)
    df.rename(columns={'geometry': 'Centroid'}, inplace=True)
    return df

#create_buffer_area - takes a list of radii and creates a buffer area based on points in a dataframe
#Need to specify the geometry column in the dataframe when defining the funciton
#When crs is set to epsg:2272, this is commonly used for the measure of feet, which can be easily converted into miles (5280ft in a mile)
#Good reference for crs is https://epsg.io
def create_buffer_area (df, geometry_col, radius_list):
    gdf = gpd.GeoDataFrame(df, geometry=geometry_col)
    gdf.to_crs(epsg=2272, inplace=True)
    rdf = gpd.GeoDataFrame()
    for r in radius_list:
        tadf = pd.merge(df,
                       gpd.GeoDataFrame(gdf.geometry.buffer(r*5280)),
                       left_index=True,
                       right_index=True)
        tadf['Radius'], tadf['Radius_Type'] = r, 'Mile'
        rdf = pd.concat([rdf,tadf])
    rdf.rename(columns={0: 'Buffer_Area'}, inplace=True)
    rdf = gpd.GeoDataFrame(rdf, geometry=geometry_col)
    rdf.to_crs(epsg=4326, inplace=True)
    return rdf

#plot_point_polygon - plots a latitude, longitudes, and trade area from a dataframe onto a map
def plot_point_polygon (df, latitude, longitude, trade_area):
    #Create base map and centers the Map
    middle_long = np.median([df[longitude]])
    middle_lat = np.median([df[latitude]])
    m = folium.Map(location=[middle_lat, middle_long], width='80%', height='80%', tiles='OpenStreetMap', zoom_start=7)
    #m = folium.Map(location=[39.828395, -98.579480], zoom_start=5)
    #Plot Latitude & Longitude
    for idx, r in df.iterrows():
        folium.Marker([r[latitude], r[longitude]]).add_to(m)
    #Plot polygons
    polys = df[trade_area]
    folium.GeoJson(polys.to_crs(epsg=4326)).add_to(m)
    return m
  
#setgeometry - quickly create a geometry column and set the crs
def setgeometry(df, geometry_variable, crs_type):
    df['geometry'] = df[geometry_variable]
    df = df.set_geometry("geometry")
    df.to_crs(epsg=crs_type, inplace=True)
    return df

#spatial_match will find points and/or radii that fall within or overlap with another radius
def spatial_match(df1,geometry1_col,df2,geometry2_col,crs_type=2272,how_type='inner'):
    df1 = setgeometry(df1,geometry1_col,crs_type)
    df2 = setgeometry(df2,geometry2_col,crs_type)
    new_df = gpd.sjoin(df1,df2,how=how_type, op='intersects')
    return new_df  
  
# ================================================================
## Loading and Formatting Dataset
df_FFR = pd.read_csv('FastFoodRestaurants.csv')
df_FFR = df_FFR[['name','address','city','province','latitude','longitude']]
df_FFR.rename(columns={'province':'state'}, inplace=True)

## Creating Data Subsets
# Mcdonalds in NY
df_MD_NY=df_FFR.loc[(df_FFR.state=='NY')&(df_FFR.name.isin(['McDonald\'s','Mcdonald\'s','McDonalds']))]
df_MD_NY.reset_index(drop=True, inplace=True)
# Burger King in NY
df_BK_NY = df_FFR.loc[(df_FFR.state=='NY') & (df_FFR.name.isin(['Burger King']))]
df_BK_NY.reset_index(drop=True, inplace=True)

# ================================================================

# Create Centroid Point from Lat/Long for both McDonalds and Burger Kings
df_MD_NY = create_point(df_MD_NY, 'longitude', 'latitude')
df_BK_NY = create_point(df_BK_NY, 'longitude', 'latitude')

# Create a 3 mile buffer area polygon around each McDonalds
radii = [3]  # list of trade area radius
df_MD_NY = create_buffer_area(df_MD_NY, 'Centroid', radii)

# Creating map
ffr_map = plot_point_polygon(df_MD_NY, 'latitude', 'longitude', 'Buffer_Area')

# Spatial Join Operation =====================================================
# Renaming columns before spatial join to avoid ambiguity
df_MD_NY.columns = ['MD_' + col for col in df_MD_NY.columns]
df_BK_NY.columns = ['BK_' + col for col in df_BK_NY.columns]

# Use spatial_match to find the Burger Kings that are located within 3 miles of McDonald’s in New York.
BK_near_MD_NY = spatial_match(df_MD_NY,'MD_Buffer_Area',df_BK_NY,'BK_Centroid')
BK_near_MD_NY = BK_near_MD_NY[['MD_latitude','MD_longitude','MD_Centroid','MD_Buffer_Area','BK_latitude','BK_longitude','BK_Centroid']]
BK_near_MD_NY.reset_index(drop=True,inplace=True)
# Marking the intersecting Burger King points ar red points in the map
for idx, r in BK_near_MD_NY.iterrows():
        folium.CircleMarker([r['BK_latitude'], r['BK_longitude']],radius=2,color='red').add_to(ffr_map)
# visualizing the map
ffr_map
