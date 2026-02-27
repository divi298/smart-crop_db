import os
import requests
import sqlite3
from flask import Flask, request, jsonify, render_template
from datetime import datetime
from database import init_db

init_db()

app = Flask(__name__)

# ==============================
# 🔐 Security Keys
# ==============================
API_KEY = os.environ.get("API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

if not API_KEY:
    print("⚠ WARNING: API_KEY not set!")

if not WEATHER_API_KEY:
    print("⚠ WARNING: WEATHER_API_KEY not set!")


# ==============================
# 🌦 Get Real Weather Data
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
            "pressure": data["main"]["pressure"],
            "rainfall": rainfall
        }

    except Exception as e:
        print("Weather API Error:", e)
        return fallback_weather()


def fallback_weather():
    return {
        "temperature": 30,
        "humidity": 60,
        "pressure": 1000,
        "rainfall": 0
    }


# ==============================
# 🌐 Dashboard Page
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

    # 🌦 Get real weather
    weather = get_weather()
    temperature = weather["temperature"]
    humidity = weather["humidity"]
    rainfall = weather["rainfall"]

    # ==============================
    # 🌱 Smart Crop Recommendation Logic
    # ==============================
    if moisture < 400 and rainfall > 2:
        soil_condition = "Very Wet"
        crop = "Rice"
        fertilizer = "Urea + DAP"

    elif 400 <= moisture < 700 and temperature > 25:
        soil_condition = "Moderate"
        crop = "Maize"
        fertilizer = "NPK 20-20-20"

    elif moisture >= 700 and rainfall < 1:
        soil_condition = "Dry"
        crop = "Millet"
        fertilizer = "Compost + Potash"

    else:
        soil_condition = "Normal"
        crop = "Groundnut"
        fertilizer = "Balanced NPK"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ==============================
    # 💾 INSERT INTO DATABASE  ✅
    # ==============================
    conn = sqlite3.connect("agri.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sensor_data 
        (moisture, temperature, humidity, rainfall, crop, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (moisture, temperature, humidity, rainfall, crop, timestamp))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "soil_condition": soil_condition,
        "recommended_crop": crop,
        "recommended_fertilizer": fertilizer
    }), 200


# ==============================
# 📊 Dashboard Data API (Now Reads from DB)
# ==============================
@app.route("/history", methods=["GET"])
def history():

    conn = sqlite3.connect("agri.db")
    cursor = conn.cursor()

    cursor.execute("SELECT moisture, temperature, humidity, rainfall, crop, timestamp FROM sensor_data ORDER BY id DESC LIMIT 50")
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
# 🌾 Yield Prediction API
# ==============================
@app.route("/predict_yield", methods=["POST"])
def predict_yield():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    land = float(data.get("land", 0))
    crop = data.get("crop", "")

    base_yields = {
        "Rice": 30,
        "Maize": 25,
        "Millet": 18,
        "Groundnut": 20
    }

    avg_yield = base_yields.get(crop, 20)
    predicted_yield = round(land * avg_yield, 2)

    return jsonify({
        "land": land,
        "crop": crop,
        "predicted_yield": predicted_yield,
        "unit": "quintals"
    }), 200


# ==============================
# 🚀 Render Production Config
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)