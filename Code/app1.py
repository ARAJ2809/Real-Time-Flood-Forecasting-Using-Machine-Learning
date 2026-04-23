"""Web app."""
import flask
from flask import Flask, render_template, request, redirect, url_for

import pickle
import base64
from training import prediction
from training.predict1 import get_weather_features
import requests
app = flask.Flask(__name__)

data = [{'name':'Delhi', "sel": "selected"}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""}, {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}]
# data = [{'name':'India', "sel": ""}]
months = [{"name":"May", "sel": ""}, {"name":"June", "sel": ""}, {"name":"July", "sel": "selected"}]
cities = [{'name':'Delhi', "sel": "selected"}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""}, {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}, {'name':'New York', "sel": ""}, {'name':'Los Angeles', "sel": ""}, {'name':'London', "sel": ""}, {'name':'Paris', "sel": ""}, {'name':'Sydney', "sel": ""}, {'name':'Beijing', "sel": ""}]

model = pickle.load(open("model.pickle", 'rb'))

def get_lat_lon(cityname):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": cityname,
        "format": "json"
    }

    headers = {
        "User-Agent": "flood-app"
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    if not data:
        raise ValueError("City not found")

    lat = float(data[0]['lat'])
    lon = float(data[0]['lon'])

    return lat, lon

@app.route("/")
@app.route('/index.html')
def index() -> str:
    """Base page."""
    return flask.render_template("index.html")

@app.route('/plots.html')
def plots():
    return render_template('plots.html')

@app.route('/heatmaps.html')
def heatmaps():
    return render_template('heatmaps.html')

@app.route('/chart.html')
def chart():
    return render_template('chart.html')

@app.route('/satellite.html')
def satellite():
    direc = "satellite_images/Delhi_July.png"
    with open(direc, "rb") as image_file:
        image = base64.b64encode(image_file.read())
    image = image.decode('utf-8')
    return render_template('satellite.html', data=data, image_file=image, months=months, text="Delhi in January 2024")

@app.route('/satellite.html', methods=['GET', 'POST'])
def satelliteimages():
    place = request.form.get('place')
    date = request.form.get('date')
    data = [{'name':'Delhi', "sel": ""}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""}, {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}]
    months = [{"name":"May", "sel": ""}, {"name":"June", "sel": ""}, {"name":"July", "sel": ""}]
    for item in data:
        if item["name"] == place:
            item["sel"] = "selected"
    
    for item in months:
        if item["name"] == date:
            item["sel"] = "selected"

    text = place + " in " + date + " 2024"

    direc = "satellite_images/{}_{}.png".format(place, date)
    with open(direc, "rb") as image_file:
        image = base64.b64encode(image_file.read())
    image = image.decode('utf-8')
    return render_template('satellite.html', data=data, image_file=image, months=months, text=text)

@app.route('/predicts.html')
def predicts():
    return render_template('predicts.html', cities=cities, cityname="Information about the city")

@app.route('/predicts.html', methods=["GET", "POST"])
def get_predicts():
    try:
        cityname = request.form["city"].strip()
        cities = [{'name':'Delhi', "sel": ""}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""}, {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}, {'name':'New York', "sel": ""}, {'name':'Los Angeles', "sel": ""}, {'name':'London', "sel": ""}, {'name':'Paris', "sel": ""}, {'name':'Sydney', "sel": ""}, {'name':'Beijing', "sel": ""}]
        for item in cities:
            if item['name'] == cityname:
                item['sel'] = 'selected'
        print(cityname)
        URL = "https://geocode.search.hereapi.com/v1/geocode"
        location = cityname
        #api_key = 'LHtLOXHyYWrAYEFNbXIQg8BM6PEY8Jryp88mmHYvAGw' # Acquire from developer.here.com
        api_key = 'pPFSt0miNxLZJY6_Zs-h-nB9W1XxxJG6s3wat1L37r8' # Acquire from developer.here.com

        PARAMS = {'apikey':api_key,'q':location} 
        # sending get request and saving the response as response object 
        r = requests.get(url = URL, params = PARAMS) 
        print(r)
        data = r.json()
        print(data)
        if not data.get("items"):
            raise ValueError("City not found in HERE API")
        latitude = data['items'][0]['position']['lat']
        longitude = data['items'][0]['position']['lng']
        print(f"Latitude: {latitude}, Longitude: {longitude}")
        api_key_weather = 'BWGMFZVJGFRMYPG92N9MNYJ9G'
        final = get_weather_features(latitude, longitude, api_key_weather)
        
        final[4] *= 15
        if str(model.predict([final])[0]) == "0":
            pred = "Safe"
        else:
            pred = "Unsafe"
        
        return render_template('predicts.html', cityname="Information about " + cityname, cities=cities, temp=round(final[0], 2), maxt=round(final[1], 2), wspd=round(final[2], 2), cloudcover=round(final[3], 2), percip=round(final[4], 2), humidity=round(final[5], 2), pred = pred)
    except Exception as e:
        print("ERROR:", e)
        return render_template(
            'predicts.html',
            cities=cities,
            cityname="Error occurred: " + str(e)
        )

if __name__ == "__main__":
    app.run(debug=True)