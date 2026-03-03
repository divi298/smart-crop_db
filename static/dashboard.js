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

            if (!data || data.length === 0) {
                console.log("No sensor data yet...");
                return;
            }

            let latest = data[data.length - 1];

            document.getElementById("moistureValue").innerText = latest.moisture;
            document.getElementById("temperatureValue").innerText = latest.temperature;
            document.getElementById("humidityValue").innerText = latest.humidity;

            let lang = document.getElementById("languageSwitcher").value;

            let crop = latest.recommended_crop;
            let soil = latest.soil_condition;
            let fertilizer = latest.recommended_fertilizer;

            // 🔹 Translate Crop
            if (lang !== "en" && dynamicTranslations.crop[crop?.toLowerCase()]) {
                crop = dynamicTranslations.crop[crop.toLowerCase()][lang] || crop;
            }

            // 🔹 Translate Soil
            if (lang !== "en" && dynamicTranslations.soil[soil?.toLowerCase()]) {
                soil = dynamicTranslations.soil[soil.toLowerCase()][lang] || soil;
            }

            document.getElementById("soil").innerText = soil;
            document.getElementById("crop").innerText = crop;
            document.getElementById("fertilizer").innerText = fertilizer;

            // ======================================
            // 🌈 INTERACTIVE FARMER ALERT SYSTEM
            // ======================================

            const moisture = latest.moisture;
            const bar = document.getElementById("moistureBar");
            const alertCard = document.getElementById("soilAlertCard");
            const alertText = document.getElementById("soilAlertText");
            const actionCard = document.getElementById("farmerAction");

            // 🌡 Moisture Progress Bar
            const percent = Math.min((moisture / 1023) * 100, 100);
            if (bar) {
                bar.style.width = percent + "%";
            }

            // 🌾 Soil Condition Visual Alerts
            if (moisture < 400) {
                alertCard.className = "soil-card soil-wet";
                alertText.innerText = "💧 Soil is Wet – Do NOT water now";
                actionCard.innerText = "⛔ Do not water. Soil already wet.";
            }
            else if (moisture < 700) {
                alertCard.className = "soil-card soil-moderate";
                alertText.innerText = "🌿 Soil is Perfect – Good condition";
                actionCard.innerText = "✅ Soil moisture is balanced.";
            }
            else {
                alertCard.className = "soil-card soil-dry";
                alertText.innerText = "⚠ Soil is Dry – Water Immediately";
                actionCard.innerText = "🚿 Please water your field today.";
            }

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