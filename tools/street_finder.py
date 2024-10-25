import requests
from io import BytesIO
from PIL import Image
import os
from main import set_environment_variables


def geocode_address(address, api_key):
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': address,
        'key': api_key
    }
    response = requests.get(geocode_url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching geocode data: {response.status_code}")

    data = response.json()
    if data['status'] != 'OK':
        raise Exception(f"Geocoding error: {data['status']}")

    location = data['results'][0]['geometry']['location']
    return location['lat'], location['lng']


def get_street_view_image(lat, lng, api_key, size="600x400", heading=0, pitch=0, fov=90):
    street_view_url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        'size': size,
        'location': f"{lat},{lng}",
        'heading': heading,
        'pitch': pitch,
        'fov': fov,
        'key': api_key
    }
    response = requests.get(street_view_url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching Street View image: {response.status_code}")

    return Image.open(BytesIO(response.content))


def main():

    set_environment_variables()

    API_KEY = os.getenv('GOOGLE_API_KEY')
    address = input("Enter the address: ")

    try:
        lat, lng = geocode_address(address, API_KEY)
        print(f"Coordinates: Latitude {lat}, Longitude {lng}")

        image = get_street_view_image(lat, lng, API_KEY)
        image.show()  # Display the image
        # To save the image, uncomment the following line:
        # image.save('street_view.jpg')

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()