import requests

def get_address_from_coords(lat, lon):
    api_key = ''
    url = f'https://api.openrouteservice.org/geocode/reverse'
    params = {
        'api_key': api_key,
        'point.lon': lon,
        'point.lat': lat,
        'size': 1  # Limit the results to 1
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'features' in data and len(data['features']) > 0:
        return data['features'][0]['properties']['label']
    return 'Unknown Location'
