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

    moisture = data.get("moisture")
    temperature = data.get("temperature")
    humidity = data.get("humidity")

    record = {
        "moisture": moisture,
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }

    sensor_history.append(record)

    if len(sensor_history) > 50:
        sensor_history.pop(0)

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

    response = {
        "soil_condition": soil_condition,
        "recommended_crop": crop,
        "recommended_fertilizer": fertilizer
    }

    return jsonify(response), 200


@app.route("/history")
def history():
    return jsonify(sensor_history)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)