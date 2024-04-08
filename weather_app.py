import requests
import json
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import os
import argparse

API_KEY = '1145a66ba4334a3887b65146240804'
BASE_URL = 'https://api.weatherapi.com/v1/current.json'  # WeatherAPI endpoint URL

# Global variables
favorites_file = 'favorites.json'
favorites = []

# Function to load favorites from file
def load_favorites():
    global favorites
    if os.path.exists(favorites_file):
        with open(favorites_file, 'r') as file:
            favorites = json.load(file)

# Function to save favorites to file
def save_favorites():
    with open(favorites_file, 'w') as file:
        json.dump(favorites, file)

# Function to add a city to favorites
def add_favorite(city_name):
    if city_name not in favorites:
        favorites.append(city_name)
        print(f'{city_name} added to favorites.')
        save_favorites()
    else:
        print(f'{city_name} is already in favorites.')

# Function to remove a city from favorites
def remove_favorite(city_name):
    if city_name in favorites:
        favorites.remove(city_name)
        print(f'{city_name} removed from favorites.')
        save_favorites()
    else:
        print(f'{city_name} is not in favorites.')

# Function to list favorite cities
def list_favorites():
    print('Favorite Cities:')
    for city in favorites:
        print(city)

# Function to fetch and display weather information for a city
def get_weather(city_name):
    params = {
        'key': API_KEY,
        'q': city_name,
        'aqi': 'no'  # Disable air quality index if not needed
    }

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        # Check if the request was successful
        if response.status_code == 200:
            temperature = data["current"]["temp_c"]
            weather_condition = data["current"]["condition"]["text"]
            humidity = data["current"]["humidity"]
            wind_speed = data["current"]["wind_kph"]
            last_updated = data["current"]["last_updated"]

            emoji = ""
            if temperature < 10:
                emoji = "❄️"  # Cold
            elif temperature >= 10 and temperature < 20:
                emoji = "⛅️"  # Moderate
            else:
                emoji = "☀️"  # Warm

            print(f'\nWeather Information for {city_name}:')
            print(f'Temperature: {temperature}°C {emoji}')
            print(f'Weather Condition: {weather_condition}')
            print(f'Humidity: {humidity}%')
            print(f'Wind Speed: {wind_speed} km/h')
            print('Last Updated:', last_updated)
        else:
            print(f'Error: {data["error"]["message"]}')
    except Exception as e:
        print(f'Error fetching weather information: {str(e)}')

# Function to auto-refresh weather information for favorite cities
def auto_refresh():
    scheduler = BackgroundScheduler()
    scheduler.start()

    for city_name in favorites:
        scheduler.add_job(
            get_weather,
            args=[city_name],
            trigger=IntervalTrigger(seconds=30),
            id=f'{city_name}_job',
            name=f'{city_name}_job',
            replace_existing=True
        )

# Main function
def main():
    parser = argparse.ArgumentParser(description='Weather Checking Application')

    parser.add_argument('--check', metavar='city', help='Check weather for a city')
    parser.add_argument('--add', metavar='city', help='Add a city to favorites')
    parser.add_argument('--remove', metavar='city', help='Remove a city from favorites')
    parser.add_argument('--list', action='store_true', help='List favorite cities')

    args = parser.parse_args()

    # Load favorites from file
    load_favorites()

    if args.check:
        get_weather(args.check)
    elif args.add:
        add_favorite(args.add)
    elif args.remove:
        remove_favorite(args.remove)
    elif args.list:
        list_favorites()
    else:
        print('Invalid command. Use --help for usage instructions.')

if __name__ == "__main__":
    main()
