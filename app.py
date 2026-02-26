import os
from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

# Get API key from Render Environment
API_KEY = os.environ.get("API_KEY")

if not API_KEY:
    print("⚠ WARNING: API_KEY not set in environment variables!")

sensor_history = []


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

    api_key_header = request.headers.get("x-api-key")

    if not api_key_header or api_key_header != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    moisture = data.get("moisture", 0)
    temperature = data.get("temperature", 0)
    humidity = data.get("humidity", 0)

    # 🌱 Crop Recommendation Logic
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

    # Base average yield per acre (simple logic)
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