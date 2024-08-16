import requests
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler

# Load the trained model
model = load_model('final_model.h5')

# Load scaler parameters
scaler_params = pd.read_csv('scaler_params.csv')
scaler_mean = scaler_params['mean'].values
scaler_scale = scaler_params['scale'].values
scaler = StandardScaler()
scaler.mean_ = scaler_mean
scaler.scale_ = scaler_scale

# Function to preprocess the data
def preprocess_data(data):
    df = pd.DataFrame(data)
    fft_features = []
    for axis in ['ax', 'ay', 'az']:
        values = df[axis].values if isinstance(df[axis], pd.Series) else [df[axis]]
        fft_vals = np.abs(np.fft.fft(values))
        fft_features.append(np.mean(fft_vals))
        fft_features.append(np.std(fft_vals))
        fft_features.append(np.max(fft_vals))
    fft_features_df = pd.DataFrame([fft_features], columns=['fft_ax_mean', 'fft_ax_std', 'fft_ax_max', 'fft_ay_mean', 'fft_ay_std', 'fft_ay_max', 'fft_az_mean', 'fft_az_std', 'fft_az_max'])
    X_scaled = scaler.transform(fft_features_df)
    return X_scaled

# Function to fetch vibration data from Flask API
def fetch_vibration_data():
    try:
        response = requests.get('http://<raspberry_pi_ip>:5000/api/vibration_data')
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Function to make predictions
def make_predictions(data):
    try:
        # Preprocess the data
        X_scaled = preprocess_data(data)
        # Make predictions
        predictions = model.predict(X_scaled)
        # Get the predicted class
        predicted_class = np.argmax(predictions, axis=1)[0]
        return int(predicted_class)
    except Exception as e:
        print(f"Error during prediction: {e}")
        return None

def main():
    # Fetch vibration data
    vibration_data = fetch_vibration_data()
    if vibration_data:
        # Make predictions
        predicted_class = make_predictions(vibration_data)
        print(f"Predicted Class: {predicted_class}")
    else:
        print("No data available for prediction.")

if __name__ == "__main__":
    main()
