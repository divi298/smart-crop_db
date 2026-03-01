import os
import sqlite3
import joblib
from flask import Flask, request, jsonify, render_template
from datetime import datetime
from database import init_db

app = Flask(__name__)

# Initialize database
init_db()

# Load ML Model
try:
    model = joblib.load("crop_model.pkl")
    print("✅ Model loaded successfully")
except:
    print("❌ Model failed to load")
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

    # Dummy environmental values
    temperature = 30
    humidity = 60
    rainfall = 0

    # Soil condition
    if moisture < 400:
        soil_condition = "Wet"
    elif moisture < 700:
        soil_condition = "Moderate"
    else:
        soil_condition = "Dry"

    # ML prediction
    if model:
        features = [[65, 50, 45, temperature, humidity, 6.5, rainfall]]
        predicted_crop = model.predict(features)[0]
    else:
        predicted_crop = "Maize"

    # Fertilizer mapping
    fertilizer_map = {
        "rice": "Urea + DAP",
        "maize": "NPK 20-20-20",
        "millet": "Compost + Potash",
        "groundnut": "Gypsum + Organic Compost",
        "muskmelon": "NPK 10-26-26",
        "cotton": "Urea + Potassium",
        "banana": "NPK 14-14-14"
    }

    fertilizer = fertilizer_map.get(
        predicted_crop.lower(),
        "Balanced NPK"
    )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert into DB
    conn = sqlite3.connect("agri.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sensor_data
        (moisture, temperature, humidity, rainfall,
         soil_condition, crop, fertilizer, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        moisture,
        temperature,
        humidity,
        rainfall,
        soil_condition,
        predicted_crop,
        fertilizer,
        timestamp
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "soil_condition": soil_condition,
        "recommended_crop": predicted_crop,
        "recommended_fertilizer": fertilizer
    })


# ==============================
# 📊 History API
# ==============================
@app.route("/history")
def history():

    conn = sqlite3.connect("agri.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT moisture, temperature, humidity, rainfall,
               soil_condition, crop, fertilizer, timestamp
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)