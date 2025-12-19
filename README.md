# Delhi Air Route Optimizer

A Django web application that helps users find optimal routes in Delhi based on air quality and distance considerations.

## Overview

Delhi Air Route Optimizer is a web-based application that combines real-time air quality data with route optimization algorithms to suggest the healthiest routes for travel within Delhi. The application allows users to:

- Find routes between any two locations in Delhi
- Optimize routes based on different priorities:
  - Shortest distance
  - Cleanest air quality
  - Balanced approach (considering both distance and air quality)
- View air quality data along different routes
- Save route history for future reference

## Features

- **Real-time Air Quality Data**: Integrates with WAQI API to fetch current air quality information
- **Intelligent Route Optimization**: Uses Dijkstra's algorithm to find optimal paths based on user preferences
- **Geocoding**: Converts addresses to coordinates for accurate routing
- **Interactive Maps**: Visualizes routes on interactive maps using Folium
- **Machine Learning Integration**: Utilizes trained models to predict air quality in areas with missing data
- **User History**: Tracks and saves route history for registered users

## Tech Stack

- **Backend**: Django 5.0.1
- **APIs**:
  - OpenRouteService for routing
  - WAQI for air quality data
- **Data Processing**:
  - NumPy
  - Pandas
  - SciPy
- **Machine Learning**:
  - Scikit-learn
- **Visualization**:
  - Folium (interactive maps)
  - Matplotlib
  - Seaborn
- **Geospatial**:
  - GeoPy

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd delhi_air_route
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   ORS_API_KEY=your_openrouteservice_api_key
   WAQI_API_KEY=your_waqi_api_key
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at `http://127.0.0.1:8000/`

## Project Structure

- **delhi_air_route/**: Main Django project settings
- **route_optimizer/**: Main application
  - **models.py**: Data models for locations and route history
  - **views.py**: View functions for handling requests
  - **services/**: Core services
    - **air_quality_service.py**: Handles air quality data retrieval
    - **routing_service.py**: Manages route calculations
    - **dijkstra_optimizer.py**: Implements route optimization algorithm
  - **templates/**: HTML templates
  - **static/**: CSS and JavaScript files
- **training/**: Machine learning model training
  - Jupyter notebooks for model training
  - Trained models and scalers
  - Visualization outputs

## Machine Learning Component

The project includes a machine learning component that:
- Predicts air quality in areas with missing data
- Analyzes patterns in air quality distribution
- Provides feature importance analysis for air quality factors
- Compares different prediction models

## Usage

1. Enter source and destination locations
2. Select routing priority (shortest, cleanest, or balanced)
3. View the suggested route on the interactive map
4. Check air quality indicators along the route
5. Save the route to history (for registered users)

## Future Enhancements

- Mobile application integration
- Real-time traffic data incorporation
- More sophisticated machine learning models
- User preferences and personalization
- Time-based air quality predictions

## License

[Specify your license here]

## Contributors

[List contributors here]