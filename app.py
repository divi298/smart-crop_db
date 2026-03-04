import os
import sqlite3
from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

DB = "agri.db"

# =========================
# Initialize DB
# =========================
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        moisture REAL,
        temperature REAL,
        humidity REAL,
        rainfall REAL,
        soil_condition TEXT,
        crop TEXT,
        fertilizer TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# Dashboard
# =========================
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# =========================
# Receive Sensor
# =========================
@app.route("/receive_sensor", methods=["POST"])
def receive_sensor():

    data = request.get_json()

    moisture = data.get("moisture",0)
    temperature = data.get("temperature",0)
    humidity = data.get("humidity",0)

    rainfall = 0

    if moisture < 400:
        soil = "Wet"
    elif moisture < 700:
        soil = "Moderate"
    else:
        soil = "Dry"

    crop = "muskmelon"
    fertilizer = "NPK 10-26-26"

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    INSERT INTO sensor_data
    (moisture,temperature,humidity,rainfall,soil_condition,crop,fertilizer,timestamp)
    VALUES(?,?,?,?,?,?,?,?)
    """,(
        moisture,
        temperature,
        humidity,
        rainfall,
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


# =========================
# History API
# =========================
@app.route("/history")
def history():

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    SELECT moisture,temperature,humidity,rainfall,
           soil_condition,crop,fertilizer,timestamp
    FROM sensor_data
    ORDER BY id DESC
    LIMIT 50
    """)

    rows = c.fetchall()
    conn.close()

    data = []

    for r in rows:
        data.append({
            "moisture":r[0],
            "temperature":r[1],
            "humidity":r[2],
            "rainfall":r[3],
            "soil_condition":r[4],
            "recommended_crop":r[5],
            "recommended_fertilizer":r[6],
            "timestamp":r[7]
        })

    return jsonify(data)

# =========================
# Run
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)