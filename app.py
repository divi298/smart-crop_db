import os
import requests
from flask import Flask, request, jsonify, render_template
from datetime import datetime

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

sensor_history = []

# ==============================
# 🌦 Get Real Weather Data
# ==============================
def get_weather():
    city = "Vijayawada,IN"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"]
        }
    except:
        # fallback values
        return {
            "temperature": 30,
            "humidity": 60,
            "pressure": 1000
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

    # ==============================
    # 🌱 Smart Crop Recommendation
    # ==============================
    if moisture < 400 and humidity > 60:
        soil_condition = "Wet"
        crop = "Rice"
        fertilizer = "Urea + DAP"
    elif moisture < 700 and temperature > 25:
        soil_condition = "Moderate"
        crop = "Maize"
        fertilizer = "NPK 20-20-20"
    else:
        soil_condition = "Dry"
        crop = "Millet"
        fertilizer = "Compost + Potash"

    record = {
        "moisture": moisture,
        "temperature": temperature,
        "humidity": humidity,
        "soil_condition": soil_condition,
        "recommended_crop": crop,
        "recommended_fertilizer": fertilizer,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    sensor_history.append(record)

    if len(sensor_history) > 50:
        sensor_history.pop(0)

    return jsonify({
        "status": "success",
        "soil_condition": soil_condition,
        "recommended_crop": crop,
        "recommended_fertilizer": fertilizer
    }), 200


# ==============================
# 📊 Dashboard Data API
# ==============================
@app.route("/history", methods=["GET"])
def history():
    return jsonify(sensor_history)


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

    # Average yield per acre (can improve later with ML)
    if crop == "Rice":
        avg_yield = 30
    elif crop == "Maize":
        avg_yield = 25
    elif crop == "Millet":
        avg_yield = 18
    else:
        avg_yield = 20

    predicted_yield = land * avg_yield

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