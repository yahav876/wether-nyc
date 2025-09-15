import requests
import json
import time
import pika
import os
from datetime import datetime
import schedule
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WeatherMonitor:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY', 'your_api_key_here')
        self.city = 'New York'
        self.country_code = 'US'
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        self.rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))
        self.rabbitmq_user = os.getenv('RABBITMQ_USER', 'admin')
        self.rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'admin123')
        self.rabbitmq_queue = 'weather_data'

    def get_weather_data(self):
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': f"{self.city},{self.country_code}",
            'appid': self.api_key,
            'units': 'metric'
        }

        try:
            measurement_time = datetime.utcnow()
            measurement_timestamp_ms = int(measurement_time.timestamp() * 1000)

            response = requests.get(url, params=params)
            response.raise_for_status()

            weather_data = response.json()

            processed_data = {
                'measurement_time_iso': measurement_time.isoformat() + 'Z',
                'measurement_timestamp_ms': measurement_timestamp_ms,
                'city': self.city,
                'country': self.country_code,
                'temperature': weather_data['main']['temp'],
                'feels_like': weather_data['main']['feels_like'],
                'humidity': weather_data['main']['humidity'],
                'pressure': weather_data['main']['pressure'],
                'weather_main': weather_data['weather'][0]['main'],
                'weather_description': weather_data['weather'][0]['description'],
                'wind_speed': weather_data.get('wind', {}).get('speed', 0),
                'wind_direction': weather_data.get('wind', {}).get('deg', 0),
                'cloudiness': weather_data['clouds']['all'],
                'visibility': weather_data.get('visibility', 0)
            }

            logging.info(f"Weather data collected at {measurement_time}: {processed_data['temperature']}°C")
            return processed_data

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching weather data: {e}")
            return None
        except KeyError as e:
            logging.error(f"Error parsing weather data: {e}")
            return None

    def send_to_rabbitmq(self, data):
        try:
            credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_password)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.rabbitmq_host,
                    port=self.rabbitmq_port,
                    credentials=credentials
                )
            )
            channel = connection.channel()

            channel.queue_declare(queue=self.rabbitmq_queue, durable=True)

            message = json.dumps(data)
            channel.basic_publish(
                exchange='',
                routing_key=self.rabbitmq_queue,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)
            )

            connection.close()
            logging.info("Data sent to RabbitMQ successfully")

        except Exception as e:
            logging.error(f"Error sending data to RabbitMQ: {e}")

    def collect_and_send(self):
        weather_data = self.get_weather_data()
        if weather_data:
            self.send_to_rabbitmq(weather_data)

    def run(self):
        logging.info("Starting Weather Monitor...")

        # Run immediately on startup
        self.collect_and_send()

        # Schedule to run every hour
        schedule.every().hour.do(self.collect_and_send)

        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    monitor = WeatherMonitor()
    monitor.run()