import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import time

st.set_page_config(page_title="Integrated Real Estate Map", layout="wide")
st.title("Integrated Real Estate Map")

# --- העלאת קובץ Excel ---
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # --- סינון Show_on_Map ---
    df = df[df['Show_on_Map'].str.lower() == 'yes']

    # --- Sidebar Filters ---
    types = df['Type'].unique().tolist()
    selected_types = st.sidebar.multiselect("Select Property Type", types, default=types)

    min_price = int(df['Price'].min())
    max_price = int(df['Price'].max())
    price_range = st.sidebar.slider("Price Range", min_price, max_price, (min_price, max_price))

    beds_list = sorted(df['Beds'].unique().tolist())
    selected_beds = st.sidebar.multiselect("Select Number of Beds", beds_list, default=beds_list)

    # --- Apply filters ---
    filtered_df = df[
        (df['Type'].isin(selected_types)) &
        (df['Price'] >= price_range[0]) &
        (df['Price'] <= price_range[1]) &
        (df['Beds'].isin(selected_beds))
    ]

    # --- יצירת מפה ---
    nyc_map = folium.Map(location=[40.7128, -74.0060], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(nyc_map)
    geolocator = Nominatim(user_agent='integrated_map_app')

    for idx, row in filtered_df.iterrows():
        # שימוש ב-Lat/Lon אם קיים
        if pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude')):
            lat, lon = row['Latitude'], row['Longitude']
        else:
            address_str = f"{row['Address']}, {row['City']}, NY"
            location = geolocator.geocode(address_str)
            if location:
                lat, lon = location.latitude, location.longitude
                time.sleep(1)
            else:
                continue

        popup_text = (f"{row['Address']} - ${row['Price']}\n"
                      f"Beds: {row['Beds']}, Baths: {row['Baths']}\nType: {row['Type']}\nNotes: {row['Notes']}")

        folium.Marker(
            location=[lat, lon],
            popup=popup_text,
            icon=folium.Icon(color=row['Color'])
        ).add_to(marker_cluster)

    # --- הצגת המפה ב-Streamlit ---
    st_folium(nyc_map, width=1000, height=600)
