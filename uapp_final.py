import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

st.set_page_config(page_title="Integrated Map", layout="wide")
st.title("Integrated Map")

# --- העלאת קובץ Excel ---
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # סינון Show_on_Map אם קיימת העמודה
    if 'Show_on_Map' in df.columns:
        df = df[df['Show_on_Map'].str.lower() == 'yes']

    # Sidebar Filters - דינמי לפי עמודות קיימות
    filters = {}
    if 'Type' in df.columns:
        types = df['Type'].unique().tolist()
        filters['Type'] = st.sidebar.multiselect("Select Property Type", types, default=types)
    if 'Price' in df.columns:
        min_price = int(df['Price'].min())
        max_price = int(df['Price'].max())
        filters['Price'] = st.sidebar.slider("Price Range", min_price, max_price, (min_price, max_price))
    if 'Beds' in df.columns:
        beds_list = sorted(df['Beds'].unique().tolist())
        filters['Beds'] = st.sidebar.multiselect("Select Number of Beds", beds_list, default=beds_list)

    # Apply filters דינמי
    filtered_df = df.copy()
    for col, val in filters.items():
        if col == 'Price':
            filtered_df = filtered_df[(filtered_df['Price'] >= val[0]) & (filtered_df['Price'] <= val[1])]
        else:
            filtered_df = filtered_df[filtered_df[col].isin(val)]

    # צבעים אוטומטיים לפי סוג נכס
    default_colors = ['blue', 'green', 'red', 'orange', 'purple', 'darkred', 'lightblue', 'cadetblue']
    type_colors = {}
    if 'Type' in df.columns:
        unique_types = df['Type'].unique()
        for i, t in enumerate(unique_types):
            type_colors[t] = default_colors[i % len(default_colors)]

    # יצירת מפה עם MarkerCluster
    nyc_map = folium.Map(location=[40.7128, -74.0060], zoom_start=12)
    marker_cluster = MarkerCluster().add_to(nyc_map)

    for idx, row in filtered_df.iterrows():
        lat, lon = row['Latitude'], row['Longitude']

        # Popup אוטומטי - כל עמודה
        popup_text = "\n".join([f"{col}: {row[col]}" for col in df.columns if col not in ['Latitude', 'Longitude']])

        # צבע Marker לפי Type או ברירת מחדל
        color = type_colors.get(row['Type'], 'blue') if 'Type' in row else 'blue'

        folium.Marker(
            location=[lat, lon],
            popup=popup_text,
            icon=folium.Icon(color=color)
        ).add_to(marker_cluster)

    # הצגת המפה ב-Streamlit
    st_folium(nyc_map, width=1000, height=600)


