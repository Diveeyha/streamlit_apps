# pip3 install ebird-api
# pip3 install streamlit
# pip3 install streamlit_folium
import streamlit as st
import pandas as pd
import datetime
import folium
from streamlit_folium import st_folium
from ebird.api import get_nearby_notable

api_key = "jfekjedvescr"
# api_key_backup="q0dg01ercg4h"

#
home = 37.369650, -76.757796
lat_m, lon_m = 37.238947, -76.745847
lat_u, lon_u = 37.5143126, -77.2074744
lat_l, lon_l = 36.9450, -76.3133

#
m = folium.Map(location=home, zoom_start=8, scrollWheelZoom=False)

#
app_title = 'RBA near me'

def main():
    st.set_page_config(app_title)
    st.title('Rare Bird Alerts Near Me')
    input_range = st.radio('Range', ['Home', 'Full Distance'])
    input_days = st.slider('Number of Days', 0, 30)  # date_filter

    #
    d_m = pd.DataFrame.from_dict(get_nearby_notable(api_key, lat_m, lon_m, dist=50))
    d_u = pd.DataFrame.from_dict(get_nearby_notable(api_key, lat_u, lon_u, dist=50))
    d_l = pd.DataFrame.from_dict(get_nearby_notable(api_key, lat_l, lon_l, dist=50))
    d_a = pd.concat([d_m, d_u, d_l])

    # make sure your date column is datetime format
    d_m['obsDt'] = pd.to_datetime(d_m['obsDt'])
    #plot_color(d_m)
    d_a['obsDt'] = pd.to_datetime(d_a['obsDt'])
    #plot_color(d_a)

    #
    if input_range == 'Home':
        folium.Circle(location=[lat_m, lon_m], fill=True, fill_color='red', radius=50000, weight=0).add_to(m)
        d_m_filtered = date_filter(d_m, input_days)

        d_m_filtered.apply(plot_markers, axis=1)
        map = st_folium(m, width=700, height=500)
    else:
        folium.Circle(location=[lat_u, lon_u], fill=True, fill_color='yellow', radius=50000, weight=0).add_to(m)
        folium.Circle(location=[lat_m, lon_m], fill=True, fill_color='red', radius=50000, weight=0).add_to(m)
        folium.Circle(location=[lat_l, lon_l], fill=True, fill_color='yellow', radius=50000, weight=0).add_to(m)
        d_a_filtered = date_filter(d_a, input_days)

        d_a_filtered.apply(plot_markers, axis=1)
        map = st_folium(m, width=700, height=500)


#
def date_filter(df, input_days):
    day_diff = datetime.datetime.today() - datetime.timedelta(days=input_days)

    # boolean indexing to filter out dates
    return df.loc[df['obsDt'] > day_diff]


#
def plot_markers(point):
    if not point.locationPrivate:
        popup = f'<a href="https://ebird.org/hotspot/{point.locId}" target="_blank">{point.locName}</a>'
        icon_color = folium.Icon(color='green')
        folium.Marker(location=[point.lat, point.lng], popup=popup, icon=icon_color).add_to(m)
    else:
        folium.Marker(location=[point.lat, point.lng], popup=point.locName, icon=folium.Icon(color="black")).add_to(m)


def plot_color(df):
    color = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
    if datetime.datetime.today() - df.loc[df['obsDt']] == 0:
        df['marker_color'] = color[0]
    elif datetime.datetime.today() - df['obsDt'] == 1:
        df['marker_color'] = color[1]
    elif 1 < (datetime.datetime.today() - df['obsDt']) <= 3:
        df['marker_color'] = color[2]
    elif 3 < (datetime.datetime.today() - df['obsDt']) <= 7:
        df['marker_color'] = color[3]
    elif 7 < (datetime.datetime.today() - df['obsDt']) <= 14:
        df['marker_color'] = color[4]
    else:
        df['marker_color'] = color[5]

# for each row I want to add a value
# to a column that uses a function that assigns a color value based
# how long ago the date was so if the date is today

# Run main
if __name__ == "__main__":
    main()
