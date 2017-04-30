from urllib2 import urlopen
import json


def geo_location(location):
    api_key = '<google api key>'
    location = location.replace(' ', '+')

    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + location\
        + '&key=' + api_key

    url_read = urlopen(url).read().decode('utf-8')
    js = json.loads(url_read)

    js_location = js['results'][0]['geometry']['location']

    return (js_location['lat'], js_location['lng'])


if __name__ == '__main__':
    location = raw_input('Enter location: ').replace(' ', '+')
    results = geo_location(location)
    print(location.title() + ' coordinates: ')
    print("Latitude: " + str(results[0]))
    print("Longitude: " + str(results[1]))
