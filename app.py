import os
import requests
import sqlite3
import joblib
from flask import Flask, request, jsonify, render_template
from datetime import datetime
from database import init_db

app = Flask(__name__)

# ==============================
# 🔐 Security Keys
# ==============================
API_KEY = os.environ.get("API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

# ==============================
# 💾 Initialize DB (Safe)
# ==============================
init_db()

# ==============================
# 🤖 Load ML Model Safely
# ==============================
try:
    model = joblib.load("crop_model.pkl")
    print("✅ Model loaded successfully")
except Exception as e:
    print("❌ Model failed to load:", e)
    model = None

# ==============================
# 🌦 Weather API
# ==============================
def get_weather():
    city = "Vijayawada,IN"

    if not WEATHER_API_KEY:
        return fallback_weather()

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return fallback_weather()

        data = response.json()

        rainfall = 0
        if "rain" in data and "1h" in data["rain"]:
            rainfall = data["rain"]["1h"]

        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "rainfall": rainfall
        }

    except:
        return fallback_weather()


def fallback_weather():
    return {
        "temperature": 30,
        "humidity": 60,
        "rainfall": 0
    }

# ==============================
# 🌐 Dashboard Route
# ==============================
@app.route("/")
def dashboard():
    try:
        return render_template("dashboard.html")
    except Exception as e:
        return f"Dashboard error: {e}"

# ==============================
# 🔐 Sensor Endpoint
# ==============================
@app.route("/receive_sensor", methods=["POST"])
def receive_sensor():

    if request.headers.get("x-api-key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    moisture = data.get("moisture", 0)

    weather = get_weather()
    temperature = weather["temperature"]
    humidity = weather["humidity"]
    rainfall = weather["rainfall"]

    district_soil = {
        "N": 65,
        "P": 50,
        "K": 45,
        "ph": 6.5
    }

    features = [[
        district_soil["N"],
        district_soil["P"],
        district_soil["K"],
        temperature,
        humidity,
        district_soil["ph"],
        rainfall
    ]]

    if model:
        predicted_crop = model.predict(features)[0]
    else:
        predicted_crop = "Model not loaded"

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

    return jsonify({
        "status": "success",
        "recommended_crop": predicted_crop,
        "soil_condition": "Predicted using ML Model",
        "recommended_fertilizer": "Apply based on soil test"
    }), 200


# ==============================
# 📊 History API
# ==============================
@app.route("/history", methods=["GET"])
def history():
    conn = sqlite3.connect("agri.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT moisture, temperature, humidity, rainfall, crop, timestamp 
        FROM sensor_data 
        ORDER BY id DESC LIMIT 50
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
# 🔄 Latest API (NEW)
# ==============================
@app.route("/latest", methods=["GET"])
def latest():
    conn = sqlite3.connect("agri.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT moisture, temperature, humidity, rainfall, crop, timestamp 
        FROM sensor_data 
        ORDER BY id DESC LIMIT 1
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
# 🚀 Production Config
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)