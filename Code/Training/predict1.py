import requests


def get_weather_features(lat, lon, api_key):
    """
    Fetch weather data from Visual Crossing and return:
    [avg_temp, max_temp, avg_wind_speed, avg_cloud_cover, total_precip, avg_humidity]
    """

    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{lat},{lon}?unitGroup=metric&key={api_key}&contentType=json"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()  # raise error for bad response
        data = response.json()

        days = data.get("days", [])
        if not days:
            raise ValueError("No weather data found")

        # Initialize values
        avg_temp = 0
        max_temp = float("-inf")
        avg_wind_speed = 0
        avg_cloud_cover = 0
        total_precip = 0
        avg_humidity = 0

        # Process data
        for day in days:
            avg_temp += day.get("temp", 0)
            max_temp = max(max_temp, day.get("tempmax", 0))
            avg_wind_speed += day.get("windspeed", 0)
            avg_cloud_cover += day.get("cloudcover", 0)
            total_precip += day.get("precip", 0)
            avg_humidity += day.get("humidity", 0)

        n = len(days)

        # Calculate averages
        avg_temp /= n
        avg_wind_speed /= n
        avg_cloud_cover /= n
        avg_humidity /= n

        features = [
            avg_temp,
            max_temp,
            avg_wind_speed,
            avg_cloud_cover,
            total_precip,
            avg_humidity,
        ]

        return features

    except requests.exceptions.RequestException as e:
        print("API Request Error:", e)
        return None
    except Exception as e:
        print("Error:", e)
        return None


# Example usage
if __name__ == "__main__":
    API_KEY = "BWGMFZVJGFRMYPG92N9MNYJ9G"  # replace this
    latitude = 37.7749
    longitude = -122.4194

    weather_features = get_weather_features(latitude, longitude, API_KEY)

    if weather_features:
        print("Weather Features:", weather_features)
    else:
        print("Failed to fetch weather data")


def testConnection():
    return "yo"