let chart;

function loadData() {
    fetch("/history")
        .then(res => res.json())
        .then(data => {

            if (data.length === 0) return;

            let latest = data[data.length - 1];

            document.getElementById("moistureValue").innerText = latest.moisture;
            document.getElementById("temperatureValue").innerText = latest.temperature;
            document.getElementById("humidityValue").innerText = latest.humidity;

            document.getElementById("soil").innerText = latest.soil_condition;
            document.getElementById("crop").innerText = latest.recommended_crop;
            document.getElementById("fertilizer").innerText = latest.recommended_fertilizer;

            updateChart(data);
        });
}

function updateChart(data) {
    let labels = data.map(d => d.timestamp);
    let moisture = data.map(d => d.moisture);

    if (chart) chart.destroy();

    chart = new Chart(document.getElementById("sensorChart"), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: "Moisture",
                data: moisture,
                borderColor: "blue"
            }]
        }
    });
}

setInterval(loadData, 5000);
loadData();