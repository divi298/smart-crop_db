import os
from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY", "farmer_secret_123")

sensor_history = []

# Dashboard Page
@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# 🔐 Secure Sensor Route
@app.route("/receive_sensor", methods=["POST"])
def receive_sensor():

    if request.headers.get("x-api-key") != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    moisture = data.get("moisture", 0)
    temperature = data.get("temperature", 0)
    humidity = data.get("humidity", 0)

    # Crop Logic
    if moisture < 400:
        soil_condition = "Wet"
        crop = "Rice"
        fertilizer = "Urea + DAP"
    elif moisture < 700:
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
        "soil_condition": soil_condition,
        "recommended_crop": crop,
        "recommended_fertilizer": fertilizer
    })


# ✅ Public for dashboard
@app.route("/history")
def history():
    return jsonify(sensor_history)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)