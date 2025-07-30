import math
import requests
from flask import jsonify, request
from math import radians, sin, cos, sqrt, atan2

def geocode_address(address):
    """
    Geocodes an address using OpenStreetMap's Nominatim API and returns latitude and longitude.
    """
    url = f'https://nominatim.openstreetmap.org/search'
    params = {
        'q': address,
        'format': 'json',
        'addressdetails': 1,
        'limit': 1
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon
        else:
            raise ValueError(f"Address '{address}' not found.")
    else:
        raise Exception("Error in geocoding request.")


# Helper function to calculate the distance between two points (Haversine formula)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (sin(dlat / 2) ** 2 +
         cos(radians(lat1)) * cos(radians(lat2)) *
         sin(dlon / 2) ** 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c  # Distance in kilometers
    print(f"Distance: {distance} km")  # Debugging line
    return distance