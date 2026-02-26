from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

sensor_history = []

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/receive_sensor", methods=["POST"])
def receive_sensor():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    moisture = data.get("moisture", 0)
    temperature = data.get("temperature", 0)
    humidity = data.get("humidity", 0)

    record = {
        "moisture": moisture,
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }

    sensor_history.append(record)

    if len(sensor_history) > 50:
        sensor_history.pop(0)

    return jsonify({"status": "success"}), 200


@app.route("/history")
def history():
    return jsonify(sensor_history)