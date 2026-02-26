let chart;

// ==============================
// 📊 Load Sensor Data
// ==============================
function loadData() {
    fetch("/history")
        .then(res => res.json())
        .then(data => {

            if (!data || data.length === 0) {
                console.log("No sensor data yet...");
                return;
            }

            let latest = data[data.length - 1];

            document.getElementById("moistureValue").innerText = latest.moisture;
            document.getElementById("temperatureValue").innerText = latest.temperature;
            document.getElementById("humidityValue").innerText = latest.humidity;

            document.getElementById("soil").innerText = latest.soil_condition;
            document.getElementById("crop").innerText = latest.recommended_crop;
            document.getElementById("fertilizer").innerText = latest.recommended_fertilizer;

            updateChart(data);
        })
        .catch(error => {
            console.error("Error fetching data:", error);
        });
}


// ==============================
// 📈 Update Chart
// ==============================
function updateChart(data) {

    let labels = data.map(d => d.timestamp);
    let moisture = data.map(d => d.moisture);

    if (chart) chart.destroy();

    chart = new Chart(document.getElementById("sensorChart"), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: "Moisture Level",
                data: moisture,
                borderColor: "blue",
                backgroundColor: "rgba(0,0,255,0.1)",
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}


// ==============================
// 🌾 Yield Prediction Function
// ==============================
function predictYield() {

    let land = document.getElementById("landInput").value;
    let crop = document.getElementById("crop").innerText;

    if (!land || land <= 0) {
        alert("Please enter valid land value.");
        return;
    }

    if (!crop || crop === "--") {
        alert("Crop recommendation not available yet.");
        return;
    }

    fetch("/predict_yield", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            land: land,
            crop: crop
        })
    })
    .then(res => res.json())
    .then(data => {

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById("yieldResult").innerText =
            "Estimated Yield: " + data.predicted_yield + " " + data.unit;
    })
    .catch(error => {
        console.error("Yield prediction error:", error);
    });
}


// ==============================
// 🔁 Auto Refresh Every 5 Sec
// ==============================
setInterval(loadData, 5000);
loadData();