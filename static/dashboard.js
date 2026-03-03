let chart;

// =====================================
// 🌍 Dynamic Translations
// =====================================
const dynamicTranslations = {
    crop: {
        rice: { te: "వరి", hi: "धान" },
        maize: { te: "మొక్కజొన్న", hi: "मक्का" },
        millet: { te: "సజ్జ", hi: "बाजरा" },
        groundnut: { te: "పల్లీలు", hi: "मूंगफली" },
        muskmelon: { te: "కర్బూజ", hi: "खरबूजा" },
        cotton: { te: "పత్తి", hi: "कपास" },
        banana: { te: "అరటి", hi: "केला" }
    },
    soil: {
        wet: { te: "తడి", hi: "गीली" },
        moderate: { te: "మధ్యస్థ", hi: "मध्यम" },
        dry: { te: "ఎండిన", hi: "सूखी" }
    }
};

// =====================================
// 📊 Load Sensor Data
// =====================================
function loadData() {

    fetch("/history")
        .then(res => res.json())
        .then(data => {

            console.log("History data:", data);

            if (!data || data.length === 0) {
                return;
            }

            // NEWEST RECORD
            let latest = data[0];

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
// =====================================
// 📈 Update Chart
// =====================================
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


// =====================================
// 🌾 Yield Prediction
// =====================================
function predictYield() {

    let land = document.getElementById("landInput").value;

    // IMPORTANT:
    // Send original English crop to backend
    // So ML logic works properly

    let displayedCrop = document.getElementById("crop").innerText;
    let originalCrop = displayedCrop;

    // Reverse translation (if Telugu or Hindi)
    for (let key in dynamicTranslations.crop) {
        let obj = dynamicTranslations.crop[key];
        if (obj.te === displayedCrop || obj.hi === displayedCrop) {
            originalCrop = key;
        }
    }

    if (!land || land <= 0) {
        alert("Please enter valid land value.");
        return;
    }

    if (!originalCrop || originalCrop === "--") {
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
            crop: originalCrop
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


// =====================================
// 🔁 Auto Refresh Every 5 Sec
// =====================================
setInterval(loadData, 5000);
loadData();