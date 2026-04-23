"""Web app."""

import flask
from flask import Flask, render_template, request
import pickle
import base64
import requests
import os
from dotenv import load_dotenv


from training.predict1 import get_weather_features

app = flask.Flask(__name__)

load_dotenv()

# Static Data
cities_list = [
    {'name': 'Delhi', "sel": "selected"},
    {'name': 'Mumbai', "sel": ""},
    {'name': 'Kolkata', "sel": ""},
    {'name': 'Bangalore', "sel": ""},
    {'name': 'Chennai', "sel": ""},
    {'name': 'New York', "sel": ""},
    {'name': 'Los Angeles', "sel": ""},
    {'name': 'London', "sel": ""},
    {'name': 'Paris', "sel": ""},
    {'name': 'Sydney', "sel": ""},
    {'name': 'Beijing', "sel": ""}
]

months = [
    {"name": "May", "sel": ""},
    {"name": "June", "sel": ""},
    {"name": "July", "sel": "selected"}
]

# Load Model
model = pickle.load(open("model.pickle", 'rb'))

# Get Latitude & Longitude (NO API KEY)
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

# Routes

@app.route("/")
@app.route('/index.html')
def index():
    return render_template("index.html")


@app.route('/plots.html')
def plots():
    return render_template('plots.html')


@app.route('/heatmaps.html')
def heatmaps():
    return render_template('heatmaps.html')


@app.route('/chart.html')
def chart():
    return render_template('chart.html')


# Satellite
@app.route('/satellite.html', methods=['GET', 'POST'])
def satellite():
    try:
        place = request.form.get('place', 'Delhi')
        date = request.form.get('date', 'July')

        text = f"{place} in {date} 2024"
        direc = f"satellite_images/{place}_{date}.png"

        with open(direc, "rb") as image_file:
            image = base64.b64encode(image_file.read()).decode('utf-8')

        return render_template(
            'satellite.html',
            data=cities_list,
            image_file=image,
            months=months,
            text=text
        )

    except Exception as e:
        print("Satellite Error:", e)
        return render_template('satellite.html', data=cities_list, months=months)


# Prediction Page (GET)
@app.route('/predicts.html')
def predicts():
    return render_template(
        'predicts.html',
        cities=cities_list,
        cityname="Information about the city"
    )


# Prediction Logic (POST)
@app.route('/predicts.html', methods=["POST"])
def get_predicts():
    try:
        cityname = request.form["city"].strip()
        print("City:", cityname)

        # Update selected city
        cities = []
        for item in cities_list:
            sel = "selected" if item['name'] == cityname else ""
            cities.append({'name': item['name'], "sel": sel})

        #Get lat/lon using OpenStreetMap
        latitude, longitude = get_lat_lon(cityname)
        print(f"Lat: {latitude}, Lon: {longitude}")

        # Get weather features
        api_key_weather = os.getenv("api_key_weather")
        final = get_weather_features(latitude, longitude, api_key_weather)

        print("Weather Features:", final)

        # ⚠️ Keep this ONLY if used during training
        final[4] *= 15

        #Prediction
        prediction = model.predict([final])[0]
        pred = "Safe" if str(prediction) == "0" else "Unsafe"

        return render_template(
            'predicts.html',
            cityname="Information about " + cityname,
            cities=cities,
            temp=round(final[0], 2),
            maxt=round(final[1], 2),
            wspd=round(final[2], 2),
            cloudcover=round(final[3], 2),
            percip=round(final[4], 2),
            humidity=round(final[5], 2),
            pred=pred
        )

    except Exception as e:
        print("ERROR:", e)
        return render_template(
            'predicts.html',
            cities=cities_list,
            cityname="Error: " + str(e)
        )


# Run App
if __name__ == "__main__":
    app.run(debug=True)