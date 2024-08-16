import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.stats import zscore, ttest_ind, ks_2samp, norm
import requests
import time
import io
from datetime import datetime

API_BASE_URL = "http://192.168.162.231:5000/api"  # Replace with your laptop's IP

def fetch_vibration_data():
    """Fetches the latest 1000 vibration data points from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/vibration_data")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None

def upload_image(image_bytes):
    """Uploads an image to the database using the API."""
    try:
        files = {'image': image_bytes}
        data = {'esp_ID': 1}
        response = requests.post(f"{API_BASE_URL}/upload_image", files=files, data=data)
        response.raise_for_status()
        print(response.json()["message"])
    except requests.RequestException as e:
        print(f"Error uploading image to API: {e}")

def read_csv_columns(directory, cols):
    """Reads columns from a CSV file."""
    data = {col: [] for col in cols}
    # Use only one normal data file
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath, usecols=cols)
            for col in cols:
                data[col].extend(df.iloc[:, cols.index(col)].tolist())
            break  # Use only the first file
    return data

def perform_fft(data, sampling_rate):
    """Performs FFT on the data."""
    N = len(data)
    yf = fft(data)
    xf = fftfreq(N, 1 / sampling_rate)
    positive_indices = np.where(xf >= 0)
    xf = xf[positive_indices]
    yf = np.abs(yf[positive_indices])
    return xf, yf

def plot_fft(xf_normal, yf_normal, xf_new, yf_new, axis_label):
    """Plots FFT comparison and returns the image as bytes."""
    plt.figure(figsize=(14, 7))
    plt.subplot(2, 1, 1)
    plt.plot(xf_normal, yf_normal)
    plt.title(f'Normal Operation - Frequency Spectrum ({axis_label})')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')

    plt.subplot(2, 1, 2)
    plt.plot(xf_new, yf_new)
    plt.title(f'New Operation - Frequency Spectrum ({axis_label})')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')

    plt.tight_layout()

    # Convert plot to image bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='jpeg')
    plt.close()
    buf.seek(0)
    return buf.getvalue()

def plot_normal_distribution(log_magnitude, label):
    """Plots normal distribution of FFT results and returns the image as bytes."""
    mean = np.mean(log_magnitude)
    std_dev = np.std(log_magnitude)
    x_values = np.linspace(min(log_magnitude), max(log_magnitude), 1000)
    pdf = norm.pdf(x_values, mean, std_dev)

    plt.figure(figsize=(14, 7))
    
    # Plot histogram
    plt.hist(log_magnitude, bins=30, density=True, alpha=0.6, color='g', label='Histogram')

    # Plot normal distribution
    plt.plot(x_values, pdf, label='Normal Distribution')
    plt.title(f'Normal Distribution of Log-Transformed FFT Results ({label})')
    plt.xlabel('Log-Magnitude')
    plt.ylabel('Probability Density')
    plt.legend()
    plt.grid(True)

    # Convert plot to image bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='jpeg')
    plt.close()
    buf.seek(0)
    return buf.getvalue()

def truncate_or_pad(data, target_length):
    """Truncates or pads the data to a target length."""
    current_length = len(data)
    if current_length > target_length:
        return data[:target_length]
    else:
        return np.pad(data, (0, target_length - current_length), 'constant')

def analyze_vibration_data():
    """Analyzes vibration data to determine if the motor is faulty."""
    directory_normal = r'/home/agya_edem/motor_data'
    cols = [1, 2, 3]
    normal_sampling_rate = 5000
    new_sampling_rate = 1000

    # Fetch new data from the API
    new_data = fetch_vibration_data()
    if new_data is None:
        print("Unable to fetch data from API. Exiting.")
        return

    # Read normal data from the first CSV file
    normal_data = read_csv_columns(directory_normal, cols)

    # Determine the minimum length for comparison
    min_length = min(len(normal_data[cols[0]]), len(new_data['ax']))

    # Truncate or pad data to ensure equal lengths
    for col, axis in zip(cols, ['ax', 'ay', 'az']):
        normal_data[col] = truncate_or_pad(normal_data[col], min_length)
        new_data[axis] = truncate_or_pad(new_data[axis], min_length)

    axis_labels = {1: 'X', 2: 'Y', 3: 'Z'}

    # Perform analysis for each axis
    image_bytes_list = []  # Store images as byte arrays
    for col, axis in zip(cols, ['ax', 'ay', 'az']):
        xf_normal, yf_normal = perform_fft(normal_data[col], normal_sampling_rate)
        xf_new, yf_new = perform_fft(new_data[axis], new_sampling_rate)

        # Generate and store FFT plot images
        image_bytes_list.append(plot_fft(xf_normal, yf_normal, xf_new, yf_new, axis_labels[col]))

        mean_yf_normal = np.mean(yf_normal)
        std_yf_normal = np.std(yf_normal)

        log_magnitude_normal = np.log1p(yf_normal)
        log_magnitude_new = np.log1p(yf_new)

        # Generate and store distribution plot images
        image_bytes_list.append(plot_normal_distribution(log_magnitude_normal, f'Normal Data ({axis_labels[col]})'))
        image_bytes_list.append(plot_normal_distribution(log_magnitude_new, f'New Data ({axis_labels[col]})'))

        z_scores = zscore(yf_new)

        outliers = np.where(np.abs(z_scores) > 3)[0]

        if len(outliers) > 0:
            print(f"Outliers detected in the operation for column {axis_labels[col]} at frequencies: {xf_new[outliers]}.")

        t_stat, p_value = ttest_ind(yf_normal, yf_new, equal_var=False)
        ks_stat, ks_p_value = ks_2samp(yf_normal, yf_new)

        if p_value < 0.05:
            print(f"Significant difference detected in FFT amplitudes for column {axis_labels[col]} (t-test p-value: {p_value}).")
        else:
            print(f"No significant difference detected for column {axis_labels[col]} (t-test p-value: {p_value}).")

        if ks_p_value < 0.05:
            print(f"Significant difference detected in FFT distributions for column {axis_labels[col]} (KS test p-value: {ks_p_value}).")
        else:
            print(f"No significant difference detected in FFT distributions for column {axis_labels[col]} (KS test p-value: {ks_p_value}).")

    # Upload first, fourth, and seventh images to the database
    selected_images = [image_bytes_list[i] for i in [0, 3, 6]]
    for image in selected_images:
        upload_image(image)

def main():
    """Main function to run the analysis every minute."""
    while True:
        analyze_vibration_data()
        time.sleep(60)  # Wait for 60 seconds before the next execution

if name == "main":
    main()