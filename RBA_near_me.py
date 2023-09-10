import streamlit as st
import pandas as pd
import folium
from datetime import date, timedelta
from streamlit_folium import st_folium
from ebird.api import get_nearby_notable
api_key = "jfekjedvescr"

#Coordinates for map center and each data pull
home = 37.369650, -76.757796
lat_m, lon_m = 37.238947, -76.745847
lat_u, lon_u = 37.5143126, -77.2074744
lat_l, lon_l = 36.9450, -76.3133

#App title
app_title = 'RBA Williamsburg'

#Pull ebird data from api and merge the dataframes
d_m = pd.DataFrame.from_dict(get_nearby_notable(api_key, lat_m, lon_m, dist=50))
d_u = pd.DataFrame.from_dict(get_nearby_notable(api_key, lat_u, lon_u, dist=50))
d_l = pd.DataFrame.from_dict(get_nearby_notable(api_key, lat_l, lon_l, dist=50))
d_a = pd.concat([d_m, d_u, d_l])

# Convert date column is datetime format
d_m['date_only'] = pd.to_datetime(d_m['obsDt']).dt.date
d_a['date_only'] = pd.to_datetime(d_a['obsDt']).dt.date


def main():
    #Page label and headers
    st.set_page_config(app_title)
    st.header('Rare Bird Alerts: Williamsburg, VA')
    st.text('By: Michelle G - September 9, 2023')
    st.text('')

    #User input options
    input_range = st.radio('Range', ['Home', 'Full Distance'])
    input_days = st.slider('Number of Days', 0, 14)  # date_filter
    tab1, tab2 = st.tabs(["Map", "Table"])

    #Assign colors to map icons
    d_m['marker_color'] = d_m.apply(plot_color, axis=1)
    d_a['marker_color'] = d_a.apply(plot_color, axis=1)

    # Filter data for small radius by user slider input #days
    d_m_filtered = date_filter(d_m, input_days)
    d_a_filtered = date_filter(d_a, input_days)

    # If smaller radius map, else larger map
    m = folium.Map(location=home, zoom_start=8, scrollWheelZoom=False)
    if input_range == 'Home':
        # Add circles and colored markers then plot map
        folium.Circle(location=[lat_m, lon_m], fill=True, fill_color='red', radius=50000, weight=0).add_to(m)
        d_m_filtered[::-1].apply(plot_markers, axis=1, args=(m,))
    else:
        # Add circles and colored markers then plot map
        folium.Circle(location=[lat_u, lon_u], fill=True, fill_color='yellow', radius=50000, weight=0).add_to(m)
        folium.Circle(location=[lat_m, lon_m], fill=True, fill_color='red', radius=50000, weight=0).add_to(m)
        folium.Circle(location=[lat_l, lon_l], fill=True, fill_color='yellow', radius=50000, weight=0).add_to(m)
        d_a_filtered[::-1].apply(plot_markers, axis=1, args=(m,))

    with tab1:
        st_folium(m, width=700, height=500)

    with tab2:
        if input_range == 'Home':
            st.table(d_m_filtered[['obsDt','howMany','comName','locName',  'obsReviewed', 'obsValid']])
        else:
            st.table(d_a_filtered[['obsDt','comName','howMany','locName','obsReviewed','obsValid']])


def date_filter(df, input_days):
    #Find difference between todays date and user input number of days
    day_diff = date.today() - timedelta(days=input_days)

    # boolean indexing to filter out dates
    return df.loc[df['date_only'] >= day_diff]


def plot_markers(point, m):
    # Add markers to map for each report
    if not point.locationPrivate:
        # Popup label and hyperlink to ebird hotspot
        popup = f'<a href="https://ebird.org/hotspot/{point.locId}" target="_blank">{point.comName}</a>'
        #Add assigned color to markers
        icon_color = folium.Icon(color=point.marker_color)
        #Add markers to map
        marker=folium.Marker(location=[point.lat, point.lng], popup=popup, icon=icon_color)
        m.add_child(marker)
    else:
        # Private ebird hotspot do not get a hyperlink and are assigned black
        icon_color = folium.Icon(color="black")
        marker=folium.Marker(location=[point.lat, point.lng], popup=point.comName, icon=icon_color)
        m.add_child(marker)


def plot_color(df):
    #Add marker colors to dataframe based on how long ago observed. More recent are red/warm colors
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


# Run main
if __name__ == "__main__":
    main()
