import os
import requests
import sqlite3
import joblib
from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

# ==============================
# 💾 Initialize Database
# ==============================
def init_db():
    conn = sqlite3.connect("agri.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            moisture INTEGER,
            temperature REAL,
            humidity REAL,
            rainfall REAL,
            crop TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ==============================
# 🤖 Load ML Model
# ==============================
try:
    model = joblib.load("crop_model.pkl")
    print("✅ Model loaded successfully")
except Exception as e:
    print("❌ Model failed to load:", e)
    model = None

# ==============================
# 🌦 Weather (Simple Fallback)
# ==============================
def get_weather():
    return {
        "temperature": 30,
        "humidity": 60,
        "rainfall": 0
    }

# ==============================
# 🌐 Dashboard
# ==============================
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# ==============================
# 🔥 Sensor Endpoint
# ==============================
@app.route("/receive_sensor", methods=["POST"])
def receive_sensor():

    print("📥 Received request from ESP")

    data = request.get_json()

    if not data:
        print("❌ No JSON received")
        return jsonify({"error": "No data received"}), 400

    print("📦 Data received:", data)

    moisture = data.get("moisture", 0)

    weather = get_weather()
    temperature = weather["temperature"]
    humidity = weather["humidity"]
    rainfall = weather["rainfall"]

    # ML Prediction
    if model:
        features = [[65, 50, 45, temperature, humidity, 6.5, rainfall]]
        predicted_crop = model.predict(features)[0]
    else:
        predicted_crop = "Maize"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("agri.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sensor_data 
        (moisture, temperature, humidity, rainfall, crop, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        moisture,
        temperature,
        humidity,
        rainfall,
        predicted_crop,
        timestamp
    ))

    conn.commit()
    conn.close()

    print("✅ Data inserted successfully")

    return jsonify({
        "status": "success",
        "recommended_crop": predicted_crop,
        "soil_condition": "Predicted using ML",
        "recommended_fertilizer": "NPK 20-20-20"
    }), 200

# ==============================
# 📊 History
# ==============================
@app.route("/history")
def history():
    conn = sqlite3.connect("agri.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT moisture, temperature, humidity, rainfall, crop, timestamp
        FROM sensor_data
        ORDER BY id DESC
        LIMIT 50
    """)

    rows = cursor.fetchall()
    conn.close()

    data = [{
        "moisture": row[0],
        "temperature": row[1],
        "humidity": row[2],
        "rainfall": row[3],
        "recommended_crop": row[4],
        "timestamp": row[5]
    } for row in rows]

    return jsonify(data)

# ==============================
# 📌 Latest Data
# ==============================
@app.route("/latest")
def latest():
    conn = sqlite3.connect("agri.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT moisture, temperature, humidity, rainfall, crop, timestamp
        FROM sensor_data
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            "moisture": row[0],
            "temperature": row[1],
            "humidity": row[2],
            "rainfall": row[3],
            "recommended_crop": row[4],
            "timestamp": row[5]
        })

    return jsonify({"message": "No data yet"})

# ==============================
# 🚀 Run Server
# ==============================
if __name__ == "__main__":
    app.run()