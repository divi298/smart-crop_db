from flask import Flask, request, jsonify, render_template, session, redirect
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "change_this_secret_key"

# 🔐 API Key (stored securely in Render environment)
API_KEY = os.getenv("API_KEY")

# Temporary storage (use database later)
sensor_history = []

# =========================
# LOGIN SYSTEM (Optional)
# =========================

USERNAME = "admin"
PASSWORD = "farmer123"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect("/")
    return render_template("login.html")


# =========================
# DASHBOARD
# =========================

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# =========================
# RECEIVE SENSOR DATA (SECURE)
# =========================

@app.route("/receive_sensor", methods=["POST"])
def receive_sensor():

    # 🔐 API Key validation
    client_key = request.headers.get("x-api-key")
    if client_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    moisture = data.get("moisture", 0)
    temperature = data.get("temperature", 0)
    humidity = data.get("humidity", 0)

    # 🔎 Validate sensor ranges
    if not (0 <= moisture <= 1024):
        return jsonify({"error": "Invalid moisture value"}), 400

    if not (0 <= temperature <= 60):
        return jsonify({"error": "Invalid temperature value"}), 400

    if not (0 <= humidity <= 100):
        return jsonify({"error": "Invalid humidity value"}), 400

    # 🧠 Crop Recommendation Logic
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

    # 📊 Store in history
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

    # Keep only last 50 records
    if len(sensor_history) > 50:
        sensor_history.pop(0)

    # 📤 Return recommendation to ESP
    return jsonify({
        "soil_condition": soil_condition,
        "recommended_crop": crop,
        "recommended_fertilizer": fertilizer
    }), 200


# =========================
# VIEW HISTORY (PROTECTED)
# =========================

@app.route("/history")
def history():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(sensor_history)