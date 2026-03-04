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

            if (!data || data.length === 0) return;

            const latest = data[0];

            // =========================
            // Update Sensor Values
            // =========================
            const moisture = document.getElementById("moistureValue");
            const temperature = document.getElementById("temperatureValue");
            const humidity = document.getElementById("humidityValue");

            if (moisture) moisture.innerText = latest.moisture ?? "--";
            if (temperature) temperature.innerText = latest.temperature ?? "--";
            if (humidity) humidity.innerText = latest.humidity ?? "--";

            // =========================
            // Update Recommendation
            // =========================
            const soil = document.getElementById("soil");
            const crop = document.getElementById("crop");
            const fertilizer = document.getElementById("fertilizer");

            if (soil) soil.innerText = latest.soil_condition ?? "--";
            if (crop) crop.innerText = latest.recommended_crop ?? "--";
            if (fertilizer) fertilizer.innerText = latest.recommended_fertilizer ?? "--";

            // =========================
            // Update Chart
            // =========================
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

    const canvas = document.getElementById("sensorChart");
    if (!canvas) return;

    const labels = data.map(d => d.timestamp);
    const moisture = data.map(d => d.moisture);

    if (chart) chart.destroy();

    chart = new Chart(canvas, {
        type: "line",
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

    const land = document.getElementById("landInput").value;

    let displayedCrop = document.getElementById("crop").innerText;
    let originalCrop = displayedCrop;

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
// 🚀 Run After Page Loads
// =====================================
document.addEventListener("DOMContentLoaded", function(){

    loadData();
    setInterval(loadData, 5000);

});