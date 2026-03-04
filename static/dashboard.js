let chart;

function loadData(){

fetch("/history")
.then(res=>res.json())
.then(data=>{

if(!data || data.length===0) return;

let latest=data[0];

document.getElementById("moistureValue").innerText=latest.moisture;
document.getElementById("temperatureValue").innerText=latest.temperature;
document.getElementById("humidityValue").innerText=latest.humidity;

document.getElementById("soil").innerText=latest.soil_condition;
document.getElementById("crop").innerText=latest.recommended_crop;
document.getElementById("fertilizer").innerText=latest.recommended_fertilizer;

updateChart(data);

})

}

function updateChart(data){

const ctx=document.getElementById("sensorChart");

let labels=data.map(d=>d.timestamp);
let moisture=data.map(d=>d.moisture);

if(chart) chart.destroy();

chart=new Chart(ctx,{
type:"line",
data:{
labels:labels,
datasets:[{
label:"Moisture",
data:moisture
}]
}
})

}

setInterval(loadData,5000);

loadData();