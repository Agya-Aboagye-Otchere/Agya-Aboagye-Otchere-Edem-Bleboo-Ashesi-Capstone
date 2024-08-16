import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime

def convert_to_binary_data(filename):
    with open(filename, 'rb') as file:
        binary_data = file.read()
    return binary_data

def get_file_modification_time(file_path):
    timestamp = os.path.getmtime(file_path)
    return datetime.fromtimestamp(timestamp)

def insert_image(conn, esp_id, reading_time, image_path):
    cursor = conn.cursor()
    sql_insert_image = """ INSERT INTO images (esp_ID, reading_time, image)
                          VALUES (%s, %s, %s)"""
    binary_data = convert_to_binary_data(image_path)
    cursor.execute(sql_insert_image, (esp_id, reading_time, binary_data))
    conn.commit()
    cursor.close()

def upload_images_to_db(folder_path, esp_id, db_config):
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            for filename in os.listdir(folder_path):
                if filename.endswith(".jpg") or filename.endswith(".png"):
                    image_path = os.path.join(folder_path, filename)
                    reading_time = get_file_modification_time(image_path)
                    insert_image(conn, esp_id, reading_time, image_path)
            print("Images uploaded successfully")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

# Database configuration
db_config = {
    'host': 'localhost',
    'port': 3307,
    'database': 'capstone_data',
    'user': 'root',
    'password': ''
}

# Folder path containing images
folder_path = r'C:\Users\234561\OneDrive - Ashesi University\Pictures\motor'
esp_id = 1  # Example ESP ID

upload_images_to_db(folder_path, esp_id, db_config)
