from google.colab import drive
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from imblearn.over_sampling import SMOTE
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import SGD
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.signal import butter, filtfilt

# Mount Google Drive
drive.mount('/content/drive')

# Function to apply a Butterworth filter
def butterworth_filter(data, cutoff, fs, order=5, filter_type='low'):
    nyquist = 0.5 * fs  # Nyquist frequency is half of the sampling rate
    normal_cutoff = cutoff / nyquist  # Normalized cutoff frequency for the filter
    b, a = butter(order, normal_cutoff, btype=filter_type, analog=False)
    y = filtfilt(b, a, data)
    return y

# Data cleaning function
def clean_vibration_data(df, fs=50000, low_cutoff=10000, high_cutoff=10):
    """
    Clean the vibration data by filtering, handling missing values, and removing outliers.
    
    :param df: DataFrame containing the vibration data in x, y, z directions.
    :param fs: Sampling frequency of the data (50 kHz in this case).
    :param low_cutoff: Low-pass filter cutoff frequency (10 kHz in this example).
    :param high_cutoff: High-pass filter cutoff frequency (10 Hz in this example).
    :return: Cleaned DataFrame.
    """
    for axis in ['ax', 'ay', 'az']:
        # Apply high-pass filter to remove low-frequency noise
        df[axis] = butterworth_filter(df[axis], high_cutoff, fs, filter_type='high')
        
        # Apply low-pass filter to remove high-frequency noise
        df[axis] = butterworth_filter(df[axis], low_cutoff, fs, filter_type='low')
        
        # Handle missing values by interpolation
        df[axis] = df[axis].interpolate(method='linear', limit_direction='both')
        
        # Remove outliers (using a simple z-score approach)
        z_scores = np.abs((df[axis] - df[axis].mean()) / df[axis].std())
        df[axis] = np.where(z_scores > 3, df[axis].median(), df[axis])
    
    return df

# Function to create the best model for multi-class classification
def create_best_multiclass_model(input_shape, num_classes):
    model = Sequential()
    model.add(Dense(units=128, activation='relu', input_shape=(input_shape,)))
    model.add(BatchNormalization())
    model.add(Dense(units=64, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dense(units=32, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(units=num_classes, activation='softmax'))  # Softmax for multi-class classification
    
    # Compile the model with the selected optimizer and learning rate
    optimizer_instance = SGD(learning_rate=0.01)
    model.compile(optimizer=optimizer_instance, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    
    return model

# Load and preprocess the data
def load_data_from_directory(directory, label, features, sample_fraction):
    data_list = []
    print(f"Loading data from directory: {directory}")
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.csv'):
                file_path = os.path.join(root, filename)
                print(f"Reading file: {file_path}")
                df = pd.read_csv(file_path, usecols=[1, 2, 3], names=features)
                
                # Clean the vibration data
                df = clean_vibration_data(df)
                
                # Check the size of the data after cleaning
                print(f"Data size after cleaning: {df.shape}")
                
                # Take a fraction of the data
                df = df.sample(frac=sample_fraction, random_state=42).reset_index(drop=True)
                df['label'] = label
                data_list.append(df)
    
    if not data_list:
        print(f"No CSV files found in directory: {directory}")
    else:
        print(f"Loaded {len(data_list)} files from {directory}")
    
    combined_df = pd.concat(data_list, ignore_index=True) if data_list else pd.DataFrame(columns=features + ['label'])
    
    # Check the size of the combined data
    print(f"Combined data size for label '{label}': {combined_df.shape}")
    
    return combined_df

def perform_fft(vibration_data):
    fft_features = []
    for axis in ['ax', 'ay', 'az']:
        values = vibration_data[axis].values if isinstance(vibration_data[axis], pd.Series) else [vibration_data[axis]]
        fft_vals = np.abs(np.fft.fft(values))
        fft_features.append(np.mean(fft_vals))
        fft_features.append(np.std(fft_vals))
        fft_features.append(np.max(fft_vals))
    return fft_features

# Define the directories for each condition
data_directories = {
    'normal': '/content/drive/My Drive/normal',
    'imbalance': '/content/drive/My Drive/imbalance',
    'vertical misalignment': '/content/drive/My Drive/vertical misalignment',
    'horizontal misalignment': '/content/drive/My Drive/horizontal misalignment',
    'underhang': '/content/drive/My Drive/underhang',
    'overhang': '/content/drive/My Drive/overhang'
}

# Define the features you are interested in
features = ['ax', 'ay', 'az']

# Define sample fractions for normal and faulty data
sample_fraction_normal = 0.15  # Adjust this fraction as needed
sample_fraction_faulty = 0.05  # Adjust this fraction as needed

# Load and combine the data with different sample fractions
combined_data = pd.DataFrame()
for label, directory in data_directories.items():
    if label == 'normal':
        sample_fraction = sample_fraction_normal  # Larger fraction for normal data
    else:
        sample_fraction = sample_fraction_faulty  # Smaller fraction for faulty data
    
    print(f"Loading data for label: {label} with sample fraction: {sample_fraction}")
    combined_data = pd.concat([combined_data, load_data_from_directory(directory, label, features, sample_fraction)], ignore_index=True)

# Check if the combined_data is empty
if combined_data.empty:
    print("Error: No data was loaded. Please check the data directories and file formats.")
else:
    # Proceed with processing and training if data is loaded
    # Perform FFT on vibration data and add as features
    print("Performing FFT on vibration data...")
    fft_features = combined_data.apply(lambda row: perform_fft(row), axis=1)
    fft_features_df = pd.DataFrame(fft_features.tolist(), columns=['fft_ax_mean', 'fft_ax_std', 'fft_ax_max', 'fft_ay_mean', 'fft_ay_std', 'fft_ay_max', 'fft_az_mean', 'fft_az_std', 'fft_az_max'])
    combined_data = pd.concat([combined_data, fft_features_df], axis=1)

    # Define final features
    final_features = ['fft_ax_mean', 'fft_ax_std', 'fft_ax_max', 'fft_ay_mean', 'fft_ay_std', 'fft_ay_max', 'fft_az_mean', 'fft_az_std', 'fft_az_max']

    # Splitting data into features and target for multi-class classification
    X = combined_data[final_features]
    y = combined_data['label']

    # Encode the labels as integers
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    # Handle class imbalance with SMOTE
    print("Applying SMOTE to balance classes...")
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y_encoded)

    # Normalize the data
    print("Normalizing the data...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_resampled)

    # Save the scaler parameters to a CSV file
    print("Saving scaler parameters...")
    scaler_params = pd.DataFrame({
        'mean': scaler.mean_,
        'scale': scaler.scale_
    })
    scaler_params.to_csv('scaler_params.csv', index=False)

    # Implementing K-Fold Cross-Validation
    kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    accuracy_scores = []
    fold = 1

    for train_idx, val_idx in kfold.split(X_scaled, y_resampled):
        print(f"Training fold {fold}...")
        X_train, X_val = X_scaled[train_idx], X_scaled[val_idx]
        y_train, y_val = y_resampled[train_idx], y_resampled[val_idx]

        # Create and train the model
        model = create_best_multiclass_model(input_shape=X_train.shape[1], num_classes=len(np.unique(y_train)))

        # Train the model and capture the history
        history = model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=30, batch_size=32, verbose=0)

        # Evaluate the model
        val_loss, val_accuracy = model.evaluate(X_val, y_val, verbose=0)
        print(f"Fold {fold} Validation Accuracy: {val_accuracy * 100:.2f}%")

        # Append the accuracy for this fold
        accuracy_scores.append(val_accuracy)
        fold += 1

    # Calculate the average accuracy across all folds
    average_accuracy = np.mean(accuracy_scores)
    print(f"Average Validation Accuracy: {average_accuracy * 100:.2f}%")

    # Final evaluation on the whole test set
    X_train_full, X_test, y_train_full, y_test = train_test_split(X_scaled, y_resampled, test_size=0.2, random_state=42)

    # Train the final model on all training data
    final_model = create_best_multiclass_model(input_shape=X_train_full.shape[1], num_classes=len(np.unique(y_train_full)))
    final_model.fit(X_train_full, y_train_full, epochs=30, batch_size=32, verbose=0)

    # Evaluate on test data
    test_loss, test_accuracy = final_model.evaluate(X_test, y_test)
    print(f'Test Accuracy: {test_accuracy * 100:.2f}%')

    # Plotting the learning curve for the last fold
    def plot_learning_curve(history):
        plt.figure(figsize=(12, 4))
        
        # Plot loss
        plt.subplot(1, 2, 1)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.title('Learning Curve - Loss')
        plt.legend()
        
        # Plot accuracy
        plt.subplot(1, 2, 2)
        plt.plot(history.history['accuracy'], label='Training Accuracy')
        plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.title('Learning Curve - Accuracy')
        plt.legend()
        
        plt.tight_layout()
        plt.show()

    # Plot the learning curve of the best model
    plot_learning_curve(history)

    # Make predictions
    print("Making predictions on test data...")
    y_pred = final_model.predict(X_test)
    y_pred = np.argmax(y_pred, axis=1)  # Get the index of the max probability

    # Classification report
    print("Generating classification report...")
    print(classification_report(y_test, y_pred))

    # Confusion matrix
    print("Generating confusion matrix...")
    cm = confusion_matrix(y_test, y_pred)
    print("Confusion Matrix:")
    print(cm)

    # Convert confusion matrix to percentages
    cm_percentage = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

    # Plotting the confusion matrix as percentages
    print("Plotting confusion matrix in percentages...")
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm_percentage, annot=True, fmt='.2f', cmap='Blues', cbar_kws={'format': '%.0f%%'})
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix (Percentages)')
    plt.show()