for idx, row in df.iterrows():
    if str(row['Show_on_Map']).lower() == 'yes':
        address_str = f"{row['Address']}, {row['City']}, NY"
        location = geolocator.geocode(address_str)
        if location:
            folium.Marker(
                location=[location.latitude, location.longitude],
                popup=f"{row['Address']} - ${row['Price']}\nBeds: {row['Beds']}, Baths: {row['Baths']}\nNotes: {row['Notes']}",
                icon=folium.Icon(color=row['Color'])
            ).add_to(nyc_map)
        else:
            print(f"Could not geocode: {address_str}")
