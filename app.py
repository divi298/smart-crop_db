import os
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
            soil_condition TEXT,
            crop TEXT,
            fertilizer TEXT,
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

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    moisture = data.get("moisture", 0)

    # Dummy weather (you can replace later)
    temperature = 30
    humidity = 60
    rainfall = 0

    # ==============================
    # 🌱 Soil Condition Logic
    # ==============================
    if moisture < 400:
        soil_condition = "Wet"
    elif moisture < 700:
        soil_condition = "Moderate"
    else:
        soil_condition = "Dry"

    # ==============================
    # 🤖 ML Crop Prediction
    # ==============================
    if model:
        # Replace with real features later
        features = [[65, 50, 45, temperature, humidity, 6.5, rainfall]]
        predicted_crop = model.predict(features)[0]
    else:
        predicted_crop = "Maize"

    # ==============================
    # 🌾 Fertilizer Mapping
    # ==============================
    fertilizer_map = {
        "rice": "Urea + DAP",
        "maize": "NPK 20-20-20",
        "millet": "Compost + Potash",
        "groundnut": "Gypsum + Organic Compost",
        "muskmelon": "NPK 10-26-26",
        "cotton": "Urea + Potassium",
        "banana": "NPK 14-14-14"
    }

    recommended_fertilizer = fertilizer_map.get(
        predicted_crop.lower(),
        "Balanced NPK"
    )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ==============================
    # 💾 Insert Into Database
    # ==============================
    conn = sqlite3.connect("agri.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sensor_data 
        (moisture, temperature, humidity, rainfall, soil_condition, crop, fertilizer, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        moisture,
        temperature,
        humidity,
        rainfall,
        soil_condition,
        predicted_crop,
        recommended_fertilizer,
        timestamp
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "soil_condition": soil_condition,
        "recommended_crop": predicted_crop,
        "recommended_fertilizer": recommended_fertilizer
    }), 200

# ==============================
# 📊 History API
# ==============================
@app.route("/history")
def history():

    conn = sqlite3.connect("agri.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT moisture, temperature, humidity, rainfall, soil_condition, crop, fertilizer, timestamp
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
        "soil_condition": row[4],
        "recommended_crop": row[5],
        "recommended_fertilizer": row[6],
        "timestamp": row[7]
    } for row in rows]

    return jsonify(data)

# ==============================
# 🚀 Run Server
# ==============================
if __name__ == "__main__":
    app.run()