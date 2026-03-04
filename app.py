import os
import sqlite3
import requests
import io

from flask import Flask, request, jsonify, render_template, send_file
from gtts import gTTS
from datetime import datetime

app = Flask(__name__)

DB = "agri.db"

API_KEY = "b049a273f64043aae3ee5f2085544ad3"
CITY = "Hyderabad"

# -----------------------------
# Initialize DB
# -----------------------------
def init_db():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        moisture REAL,
        temperature REAL,
        humidity REAL,
        soil_condition TEXT,
        crop TEXT,
        fertilizer TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# Dashboard
# -----------------------------
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# -----------------------------
# Receive Sensor Data
# -----------------------------
@app.route("/receive_sensor", methods=["POST"])
def receive_sensor():

    data = request.get_json()

    moisture = data.get("moisture")
    temperature = data.get("temperature")
    humidity = data.get("humidity")

    # ----------------------------
    # Soil condition
    # ----------------------------

    if moisture < 400:
        soil = "Wet"
    elif moisture < 700:
        soil = "Moderate"
    else:
        soil = "Dry"

    # ----------------------------
    # Dynamic Crop Recommendation
    # ----------------------------

    if soil == "Wet" and temperature > 25:
        crop = "Rice"
        fertilizer = "Urea"

    elif soil == "Moderate" and 20 <= temperature <= 32:
        crop = "Maize"
        fertilizer = "NPK 20-20-0"

    elif soil == "Dry" and temperature > 30:
        crop = "Millet"
        fertilizer = "DAP"

    elif humidity > 70:
        crop = "Banana"
        fertilizer = "Potassium Fertilizer"

    else:
        crop = "Groundnut"
        fertilizer = "NPK 10-26-26"

    # ----------------------------
    # Save data
    # ----------------------------

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    INSERT INTO sensor_data
    (moisture,temperature,humidity,soil_condition,crop,fertilizer,timestamp)
    VALUES(?,?,?,?,?,?,?)
    """,(
        moisture,
        temperature,
        humidity,
        soil,
        crop,
        fertilizer,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "status":"success",
        "soil_condition":soil,
        "recommended_crop":crop,
        "recommended_fertilizer":fertilizer
    })
# -----------------------------
# History API
# -----------------------------
@app.route("/history")
def history():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    SELECT moisture,temperature,humidity,
           soil_condition,crop,fertilizer,timestamp
    FROM sensor_data
    ORDER BY id DESC
    LIMIT 20
    """)

    rows = c.fetchall()
    conn.close()

    data = []

    for r in rows:

        data.append({
            "moisture":r[0],
            "temperature":r[1],
            "humidity":r[2],
            "soil_condition":r[3],
            "recommended_crop":r[4],
            "recommended_fertilizer":r[5],
            "timestamp":r[6]
        })

    return jsonify(data)

# -----------------------------
# Weather API
# -----------------------------
@app.route("/weather")
def weather():

    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

    res = requests.get(url).json()

    return jsonify({
        "temperature":res["main"]["temp"],
        "humidity":res["main"]["humidity"],
        "weather":res["weather"][0]["main"]
    })

# -----------------------------
# Yield Prediction
# -----------------------------
@app.route("/predict_yield", methods=["POST"])
def predict_yield():

    data = request.get_json()

    crop = data["crop"]
    land = float(data["land"])

    yield_map = {
        "rice":3.5,
        "maize":2.8,
        "banana":30,
        "muskmelon":2.5,
        "cotton":2
    }

    yield_per_acre = yield_map.get(crop,2)

    predicted = yield_per_acre * land

    return jsonify({
        "predicted_yield":round(predicted,2),
        "unit":"tons"
    })

# -----------------------------
# Voice Recommendation
# -----------------------------
@app.route("/speak", methods=["POST"])
def speak():

    data = request.get_json()

    crop = data.get("crop")
    fertilizer = data.get("fertilizer")
    soil = data.get("soil")
    language = data.get("language","en")

    # ----------------------------
    # Crop Translations
    # ----------------------------

    crop_te = {
        "Rice":"వరి",
        "Maize":"మొక్కజొన్న",
        "Millet":"సజ్జ",
        "Banana":"అరటి",
        "Groundnut":"పల్లీలు"
    }

    crop_hi = {
        "Rice":"धान",
        "Maize":"मक्का",
        "Millet":"बाजरा",
        "Banana":"केला",
        "Groundnut":"मूंगफली"
    }

    soil_te = {
        "Wet":"తడి",
        "Moderate":"మధ్యస్థ",
        "Dry":"ఎండిన"
    }

    soil_hi = {
        "Wet":"गीली",
        "Moderate":"मध्यम",
        "Dry":"सूखी"
    }

    # ----------------------------
    # Language Messages
    # ----------------------------

    if language == "te":

        crop = crop_te.get(crop,crop)
        soil = soil_te.get(soil,soil)

        text = f"సిఫార్సు చేసిన పంట {crop}. మట్టి పరిస్థితి {soil}. ఉపయోగించవలసిన ఎరువు {fertilizer}"

    elif language == "hi":

        crop = crop_hi.get(crop,crop)
        soil = soil_hi.get(soil,soil)

        text = f"अनुशंसित फसल {crop} है। मिट्टी की स्थिति {soil} है। उपयोग करने वाला उर्वरक {fertilizer}"

    else:

        text = f"Recommended crop is {crop}. Soil condition is {soil}. Use fertilizer {fertilizer}"

    # ----------------------------
    # Convert text to speech
    # ----------------------------

    tts = gTTS(text=text, lang=language)

    audio = io.BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)

    return send_file(audio, mimetype="audio/mpeg")
# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":

    port = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)