import requests

def get_address_from_coords(lat, lon):
    api_key = '5b3ce3597851110001cf6248f3302b270ec94f7286a9bdde2335bc24'
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
