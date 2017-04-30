#!/usr/bin/python
from urllib2 import urlopen
import json
from geocode import geo_location

fs_client_id = '<foursquare client id>'
fs_client_secret = '<foursquare client secret>'


def find_restaurant(meal, location):
    coords = geo_location(location)
    lat = coords[0]
    lng = coords[1]

    url = 'https://api.foursquare.com/v2/venues/search?client_id={0}&client_secret=\
{1}&ll={2},{3}&query={4}&v=20140806&m=foursquare&locale=en'.format(fs_client_id, fs_client_secret, lat, lng, meal)

    url_read = urlopen(url).read().decode('utf-8')
    js = json.loads(url_read)

    if js['response']['venues']:
        js_first = js['response']['venues'][0]

        try:
            id = js_first['id']
            name = js_first['name']
        except:
            id = None
            name = "No restaurants found."

        image_request_url = 'https://api.foursquare.com/v2/venues/{0}/photos?client_id={1}&v=20140806&client_secret={2}'.format(id, fs_client_id, fs_client_secret)
        image_url_read = urlopen(image_request_url).read().decode('utf-8')
        image_js = json.loads(image_url_read)

        try:
            first = image_js['response']['photos']['items'][0]
            pref = first['prefix']
            suff = first['suffix']
            image_url = pref + "300x300" + suff
        except:
            image_url = "No image found."

        try:
            address = js_first['location']['address']
        except:
            address = "Address not found."

        return {'name': name, 'address': address, 'image': image_url}
    else:
        return {'error': 'No restaurants found.'}


if __name__ == '__main__':
    meal = raw_input("What would you like to eat?: ")
    location = raw_input("Enter city and country: ")
    find_restaurant(meal, location)
