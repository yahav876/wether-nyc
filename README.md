# NYC Weather Monitoring System

A comprehensive weather monitoring system that collects NYC weather data every hour using the OpenWeatherMap API and stores it in Elasticsearch via RabbitMQ and Logstash, with Grafana for visualization.

## Architecture

- **Weather Monitor**: Python app that fetches weather data every hour with millisecond precision timestamps
- **RabbitMQ**: Message broker for reliable data transport
- **Logstash**: Data processing pipeline that collects from RabbitMQ and sends to Elasticsearch
- **Elasticsearch**: Data storage and indexing
- **Kibana**: Elasticsearch data exploration and visualization interface
- **Grafana**: Data visualization and dashboards

## Prerequisites

- Docker and Docker Compose
- OpenWeatherMap API key (free at https://openweathermap.org/api)

## Setup Instructions

1. **Clone and navigate to the project directory**
   ```bash
   git clone <repository-url>
   cd wether-nyc
   ```

2. **Set up environment variables**
   ```bash
   # Create .env file with your OpenWeatherMap API key
   echo "OPENWEATHER_API_KEY=your_api_key_here" > .env
   # Replace 'your_api_key_here' with your actual API key from https://openweathermap.org/api
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Verify services are running**
   ```bash
   docker-compose ps
   ```

## Service Access

- **Grafana Dashboard**: http://localhost:3000 (admin/admin123)
- **Kibana Dashboard**: http://localhost:5601 (no authentication required)
- **RabbitMQ Management**: http://localhost:15672 (admin/admin123)
- **Elasticsearch**: http://localhost:9200

## Data Collection

The system automatically:
- Collects weather data every hour
- Records exact measurement timestamps in milliseconds
- Stores comprehensive weather metrics including temperature, humidity, pressure, wind, and visibility
- Creates daily indices in Elasticsearch (weather-data-YYYY.MM.DD)

## Grafana Dashboard

The pre-configured dashboard includes:
- Current temperature display
- Temperature trends over time
- Humidity levels
- Recent weather conditions table

## Monitoring

Check logs for any service:
```bash
docker-compose logs -f weather-monitor
docker-compose logs -f logstash
```

## Stopping the System

```bash
docker-compose down
```

To remove all data:
```bash
docker-compose down -v
```