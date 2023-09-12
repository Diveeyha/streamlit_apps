import streamlit as st
import pandas as pd
import folium
from datetime import date, timedelta
from streamlit_folium import st_folium
from ebird.api import get_nearby_notable
api_key = "jfekjedvescr"

# Coordinates for map center and each data pull
lat_m, lon_m = 37.238947, -76.745847
lat_u, lon_u = 37.5143126, -77.2074744
lat_l, lon_l = 36.9450, -76.3133


@st.cache_data(ttl=5*60)
def load_merged_data():
    df1 = load_data(lat_m, lon_m)
    df2 = load_data(lat_l, lon_l)
    df3 = load_data(lat_u, lon_u)
    df_all = pd.concat([df1, df2, df3])
    return df_all


@st.cache_data(ttl=5*60)
def load_data(lat, lng):
    # Pull eBird data from api and merge the dataframes
    df = pd.DataFrame.from_dict(get_nearby_notable(api_key, lat, lng, dist=50))
    df['date_only'] = pd.to_datetime(df['obsDt']).dt.date
    # Assign colors to map icons
    df['marker_color'] = df.apply(plot_color, axis=1)
    return df


@st.cache_data
def plot_color(df):
    # Add marker colors to dataframe based on how long ago observed. More recent are red/warm colors
    color = ['red', 'orange', 'green', 'blue', 'purple']
    total_days = date.today() - df['date_only']
    if df['date_only'] == date.today():
        return color[0]
    elif total_days == timedelta(days=1):
        return color[1]
    elif timedelta(days=1) < total_days <= timedelta(days=3):
        return color[2]
    elif timedelta(days=3) < total_days <= timedelta(days=7):
        return color[3]
    elif timedelta(days=7) < total_days <= timedelta(days=14):
        return color[4]
    else:
        return "white"


@st.cache_data
def date_filter(df, input_days):
    # Find difference between today's date and user input number of days
    day_diff = date.today() - timedelta(days=input_days)

    # boolean indexing to filter out dates
    return df.loc[df['date_only'] >= day_diff]


@st.cache_resource
def map_call(on, d_m_filtered, d_a_filtered):
    # If smaller radius map, else larger map
    # figure = folium.Figure(width="100%", height="50%")
    figure_map = folium.Map(location=[lat_m, lon_m], zoom_start=8, scrollWheelZoom=False, width='100%',
                            height='5%')  # .add_to(figure)
    if not on:
        # Add circles and colored markers then plot map
        folium.Circle(location=[lat_m, lon_m], fill=True, fill_color='red', radius=50000, weight=0).add_to(
            figure_map)
        d_m_filtered[::-1].apply(plot_markers, axis=1, args=(figure_map,))
    else:
        # Add circles and colored markers then plot map
        folium.Circle(location=[lat_u, lon_u], fill=True, fill_color='yellow', radius=50000, weight=0).add_to(
            figure_map)
        folium.Circle(location=[lat_m, lon_m], fill=True, fill_color='red', radius=50000, weight=0).add_to(
            figure_map)
        folium.Circle(location=[lat_l, lon_l], fill=True, fill_color='yellow', radius=50000, weight=0).add_to(
            figure_map)
        d_a_filtered[::-1].apply(plot_markers, axis=1, args=(figure_map,))
    return figure_map


def plot_markers(point, _figure_map):
    # Add markers to map for each report
    if not point.locationPrivate:
        # Popup label and hyperlink to eBird hotspot
        popup = f'<a href="https://ebird.org/hotspot/{point.locId}" target="_blank">{point.comName}</a>'
        # Add assigned color to markers
        icon_color = folium.Icon(color=point.marker_color)
        # Add markers to map
        marker = folium.Marker(location=[point.lat, point.lng], popup=popup, icon=icon_color)
        _figure_map.add_child(marker)
    else:
        # Private eBird hotspot do not get a hyperlink and are assigned black
        icon_color = folium.Icon(color="black")
        marker = folium.Marker(location=[point.lat, point.lng], popup=point.comName, icon=icon_color)
        _figure_map.add_child(marker)


def main():
    # Page label and headers
    st.header('RBA Williamsburg')
    # st.text('By: Michelle G - September 9, 2023')

    # User input options
    on = st.toggle('Full Distance')
    input_days = st.slider('Number of Days', 0, 10)  # date_filter

    d_m = load_data(lat_m, lon_m)
    d_a = load_merged_data()

    # Filter data for small radius by user slider input #days
    d_m_filtered = date_filter(d_m, input_days)
    d_a_filtered = date_filter(d_a, input_days)

    with st.expander("Map"):
        complete_map = map_call(on, d_m_filtered, d_a_filtered)
        st_folium(complete_map, height=350)  # width=700, height=500

    with st.expander("Table"):
        if not on:
            st.table(d_m_filtered[['obsDt', 'howMany', 'comName', 'locName', 'obsReviewed', 'obsValid']])
        else:
            st.table(d_a_filtered[['obsDt', 'comName', 'howMany', 'locName', 'obsReviewed', 'obsValid']])


# Run main
if __name__ == "__main__":
    main()
