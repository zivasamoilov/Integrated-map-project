import pandas as pd
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
import time

# קריאת נתונים
df = pd.read_excel('template.xlsx')

# יצירת מפה
nyc_map = folium.Map(location=[40.7128, -74.0060], zoom_start=12)

geolocator = Nominatim(user_agent='integrated_map_app')

# יצירת MarkerCluster
marker_cluster = MarkerCluster().add_to(nyc_map)

# סינון ראשוני לפי Show_on_Map
df = df[df['Show_on_Map'].str.lower() == 'yes']

# הוספת נכסים למפה
for idx, row in df.iterrows():
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
            print(f"Could not geocode: {address_str}")
            continue

    popup_text = (f"{row['Address']} - ${row['Price']}\n"
                  f"Beds: {row['Beds']}, Baths: {row['Baths']}\n"
                  f"Type: {row['Type']}\nNotes: {row['Notes']}")

    folium.Marker(
        location=[lat, lon],
        popup=popup_text,
        icon=folium.Icon(color=row['Color'])
    ).add_to(marker_cluster)

# שמירה למפה HTML
nyc_map.save('integrated_map_cluster.html')
print('Interactive cluster map generated: integrated_map_cluster.html')
