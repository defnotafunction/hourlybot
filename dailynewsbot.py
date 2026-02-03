import requests
from newsapi import NewsApiClient
import os
from gtts import gTTS
import tempfile
import schedule
import time
import random
from datetime import datetime
import ctypes

ctypes.windll.kernel32.SetThreadExecutionState(
    0x80000002  # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
)

news_client = NewsApiClient(api_key='210c755c62e64b30b0eb27894e818546')

APIKEY = '9d57377ac52a5cbb61acb342133b006b'
weather_endpoint = f'https://api.openweathermap.org/data/2.5/weather?lat=38.782712&lon=-90.841455&units=imperial&appid={APIKEY}'


def get_top_headlines():
    top_headlines = news_client.get_top_headlines(
                                            category='general',
                                            language='en',
                                            country='us')

    return top_headlines

def get_random_headline():
    top_articles = get_top_headlines()['articles']
    random_article = random.choice(top_articles)
    return random_article

def get_random_headline_formatted():
    random_article = get_random_headline()
    title = random_article['title']
    description = random_article['description'] or "No description available."
    publisher = random_article['source']['name']

    return f"""
            Your hourly news, which is from {publisher}, is this:
            "{title}".
            What follows is a brief description of the article:
            {description}
            """

def get_current_weather():
    request = requests.get(weather_endpoint)
    return request.json()

def get_current_weather_formatted():
    weather = get_current_weather()
    main_information = weather['main']
    desc = weather['weather'][0]['description']
    wind_speed = weather['wind']['speed']
    return f"""
            Expect {desc} this hour.
            The temperature is {round(main_information['temp'])} degrees fahrenheit;
            it feels like {round(main_information['feels_like'])} degrees fahrenheit.
            Winds are at a speed of {wind_speed} miles per hour,
            and the humidity is {main_information['humidity']}%
            """

def provide_hourly_info():
    weather_info = get_current_weather_formatted()
    news_info = get_random_headline_formatted()

    return f"""
            Hello! It's time for your hourly update.
            First, the weather.
            {weather_info}
            Next, is the news.
            {news_info}

            That is all.

           """

def play_message(message):
    global last_audio_time
    last_audio_time = time.time()


    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        filename = tmp_file.name

    tts = gTTS(message, lang='en', slow=True)
    tts.save(filename)


    os.system(f'start /wait "" "{filename}"')

    time.sleep(100)

    delete_file(filename)

def delete_file(filename):
    os.remove(filename)

def is_quiet_hours():
    hour = datetime.now().hour
    return hour >= 23 or hour < 5

def hourly_job():
    if is_quiet_hours():
        return 

    play_message(provide_hourly_info())

def keep_speaker_alive():
    os.system(
        'powershell -c (New-Object Media.SoundPlayer "C:\\Windows\\Media\\Windows Background.wav").PlaySync()'
    )

hourly_job()

schedule.every().hour.at(":00").do(hourly_job)
schedule.every().hour.at(":30").do(hourly_job)

while True:
    schedule.run_pending()
    time.sleep(1)

    if time.time() - last_audio_time > 300: # 5 minutes 
        keep_speaker_alive()
        last_audio_time = time.time()

