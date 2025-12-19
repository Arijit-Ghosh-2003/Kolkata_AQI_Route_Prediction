# Air Quality Route Optimizer for Kolkata

## Data Sources and APIs

### 1. Air Quality Data
- **WAQI API**: The project uses the World Air Quality Index (WAQI) API to fetch real-time air quality data.
  - API Endpoint: https://api.waqi.info
  - Documentation: https://aqicn.org/api/
  - Data provided: PM2.5, PM10, NO2, CO, O3 and overall AQI values
  - Implementation: See `route_optimizer/services/air_quality_service.py`

### 2. Routing Data
- **OpenRouteService API**: Used for geocoding addresses and calculating optimal routes.
  - API Endpoint: https://api.openrouteservice.org
  - Documentation: https://openrouteservice.org/dev/#/api-docs
  - Features used: Geocoding, Directions
  - Implementation: See `route_optimizer/services/routing_service.py`

## Air Quality Forecasting Models

### Current Implementation
The project uses a machine learning model for air quality forecasting with the following characteristics:

1. **Model Type**: Random Forest Regressor (based on files in the training directory)
2. **Features Used**:
   - Historical AQI data for PM2.5, PM10, NO2, CO, O3
   - Weather data (temperature, humidity, wind speed)
   - Time-based features (hour of day, day of week, month)

3. **Training Process**:
   - Data preprocessing and feature engineering in `training/air_quality_model_training.ipynb`
   - Model selection through comparison of multiple algorithms
   - Hyperparameter tuning using grid search
   - Model evaluation using RMSE, MAE, and R² metrics

4. **Model Files**:
   - Trained model: `training/aqi_prediction_model.pkl`
   - Feature scaler: `training/feature_scaler.pkl`
   - Feature importance: `training/feature_importance.csv`

## Implementing Alternative Models

To implement a new air quality forecasting model in the future:

1. **Create a New Model Class**:
   - Create a new Python file in `route_optimizer/services/models/`
   - Implement a class that follows the same interface as the current model

2. **Model Interface Requirements**:
   ```python
   class NewAirQualityModel:
       def __init__(self, model_path=None):
           # Load your model and any required preprocessing components
           pass
           
       def predict(self, features):
           # Process features and return predictions
           pass
           
       def get_feature_importance(self):
           # Return feature importance if applicable
           pass
   ```

3. **Training Process**:
   - Create a new Jupyter notebook in the `training/` directory
   - Follow the data preprocessing steps from the existing notebook
   - Train your new model (e.g., Neural Network, XGBoost, etc.)
   - Save the model and any preprocessing components
   
4. **Integration**:
   - Update the `AirQualityService` class to use your new model
   - Modify the `settings.py` to include a configuration option for selecting models
   - Update any UI components to reflect new model capabilities

5. **Evaluation**:
   - Compare the new model's performance with the existing model
   - Document performance metrics and improvements

## Model Selection Configuration

To enable easy switching between different models, add the following to `settings.py`:

```python
# Air Quality Model Configuration
AQ_MODEL_CONFIG = {
    'model_type': 'random_forest',  # Options: 'random_forest', 'neural_network', 'xgboost', etc.
    'model_path': 'path/to/model/file.pkl',
    'scaler_path': 'path/to/scaler/file.pkl',
}
```

Then modify the `AirQualityService` to use the selected model based on configuration.