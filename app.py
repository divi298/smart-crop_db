import os
import requests
import sqlite3
import joblib
from flask import Flask, request, jsonify, render_template
from datetime import datetime
from database import init_db

# Initialize DB
init_db()

app = Flask(__name__)

# ==============================
# 🔐 Security Keys
# ==============================
API_KEY = os.environ.get("API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

# ==============================
# 🤖 Load ML Model
# ==============================
model = joblib.load("crop_model.pkl")

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
# 🌐 Dashboard
# ==============================
@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# ==============================
# 🔐 Secure Sensor Endpoint
# ==============================
@app.route("/receive_sensor", methods=["POST"])
def receive_sensor():

    if request.headers.get("x-api-key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    moisture = data.get("moisture", 0)

    # 🌦 Get weather
    weather = get_weather()
    temperature = weather["temperature"]
    humidity = weather["humidity"]
    rainfall = weather["rainfall"]

    # ==============================
    # 🧪 Simulated Soil Data (District-based)
    # ==============================
    district_soil = {
        "N": 65,
        "P": 50,
        "K": 45,
        "ph": 6.5
    }

    # ==============================
    # 🤖 ML Prediction
    # ==============================
    features = [[
        district_soil["N"],
        district_soil["P"],
        district_soil["K"],
        temperature,
        humidity,
        district_soil["ph"],
        rainfall
    ]]

    predicted_crop = model.predict(features)[0]

    soil_condition = "Predicted using ML Model"
    fertilizer = "Apply based on soil test recommendation"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ==============================
    # 💾 Store in Database
    # ==============================
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
        "soil_condition": soil_condition,
        "recommended_fertilizer": fertilizer
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

    data = []
    for row in rows:
        data.append({
            "moisture": row[0],
            "temperature": row[1],
            "humidity": row[2],
            "rainfall": row[3],
            "recommended_crop": row[4],
            "timestamp": row[5]
        })

    return jsonify(data)


# ==============================
# 🌾 Yield Prediction
# ==============================
@app.route("/predict_yield", methods=["POST"])
def predict_yield():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    land = float(data.get("land", 0))
    crop = data.get("crop", "")

    base_yields = {
        "rice": 30,
        "maize": 25,
        "millet": 18,
        "groundnut": 20
    }

    avg_yield = base_yields.get(crop.lower(), 20)
    predicted_yield = round(land * avg_yield, 2)

    return jsonify({
        "land": land,
        "crop": crop,
        "predicted_yield": predicted_yield,
        "unit": "quintals"
    }), 200


# ==============================
# 🚀 Production Config
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)