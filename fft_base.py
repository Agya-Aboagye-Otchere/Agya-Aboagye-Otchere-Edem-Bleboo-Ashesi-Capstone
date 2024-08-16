from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",  # Localhost because it's running on the same machine
        user="root",
        password="",  # Your MySQL password
        database="capstone_data",
        port=3307
    )
    return conn

@app.route('/api/vibration_data', methods=['GET'])
def fetch_vibration_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        SELECT ax, ay, az FROM vibration 
        ORDER BY reading_time DESC LIMIT 1000;
        """  # Fetch latest 1000 samples for each axis
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        data = {"ax": [row[0] for row in rows], "ay": [row[1] for row in rows], "az": [row[2] for row in rows]}
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    try:
        esp_ID = request.form.get('esp_ID', type=int)
        image_data = request.files['image'].read()
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO fft_images (esp_ID, image, reading_time) VALUES (%s, %s, NOW())
        """
        cursor.execute(query, (esp_ID, image_data))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Image uploaded successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
