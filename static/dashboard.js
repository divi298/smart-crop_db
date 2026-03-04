let chart;
let currentWeather = "Clear";

/* =====================================
🌍 MULTILINGUAL TRANSLATIONS
===================================== */

const translations = {

en:{
dashboard_title:"🌾 Smart Crop IoT Dashboard",
live_status:"📡 Live Field Status",
moisture:"Soil Moisture",
temperature:"Temperature",
humidity:"Humidity",
crop_rec:"Crop Recommendation",
soil:"Soil Condition:",
crop:"Recommended Crop:",
fertilizer:"Fertilizer:",
moisture_chart:"Moisture Trend"
},

te:{
dashboard_title:"🌾 స్మార్ట్ క్రాప్ ఐఓటి డాష్‌బోర్డ్",
live_status:"📡 ప్రత్యక్ష పొల స్థితి",
moisture:"మట్టిలో తేమ",
temperature:"ఉష్ణోగ్రత",
humidity:"ఆర్ద్రత",
crop_rec:"పంట సూచన",
soil:"మట్టి పరిస్థితి:",
crop:"సిఫార్సు చేసిన పంట:",
fertilizer:"ఎరువు:",
moisture_chart:"తేమ మార్పు గ్రాఫ్"
},

hi:{
dashboard_title:"🌾 स्मार्ट क्रॉप IoT डैशबोर्ड",
live_status:"📡 खेत की लाइव स्थिति",
moisture:"मिट्टी की नमी",
temperature:"तापमान",
humidity:"आर्द्रता",
crop_rec:"फसल सिफारिश",
soil:"मिट्टी की स्थिति:",
crop:"अनुशंसित फसल:",
fertilizer:"उर्वरक:",
moisture_chart:"नमी ग्राफ"
}

};


/* =====================================
🌐 LANGUAGE SWITCH
===================================== */

function changeLanguage(){

const lang=document.getElementById("languageSelector").value;

localStorage.setItem("language",lang);

document.querySelectorAll("[data-key]").forEach(element=>{

const key=element.getAttribute("data-key");

if(translations[lang][key]){
element.innerText=translations[lang][key];
}

});

}


window.addEventListener("DOMContentLoaded",()=>{

const savedLang=localStorage.getItem("language") || "en";

document.getElementById("languageSelector").value=savedLang;

changeLanguage();

});


/* =====================================
🌦 LOAD WEATHER
===================================== */

function loadWeather(){

fetch("/weather")
.then(res=>res.json())
.then(data=>{

currentWeather = data.weather;

if(document.getElementById("weatherCondition")){
document.getElementById("weatherCondition").innerText=data.weather;
}

if(document.getElementById("weatherTemp")){
document.getElementById("weatherTemp").innerText=data.temperature+" °C";
}

})
.catch(err=>console.error("Weather error:",err));

}


/* =====================================
🚿 SMART IRRIGATION ADVICE
===================================== */

function irrigationAdvice(moisture){

let message="";

if(moisture < 400){
message="🚿 Soil is very wet — Avoid irrigation";
}
else if(moisture > 700){
message="💧 Soil is dry — Irrigation recommended";
}
else if(currentWeather==="Rain"){
message="🌧 Rain expected — Do not irrigate";
}
else{
message="🌱 Soil moisture is healthy";
}

document.getElementById("farmerAction").innerText=message;

}


/* =====================================
📡 LOAD SENSOR DATA
===================================== */

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


/* progress bar */

let moisturePercent=Math.min(100,(latest.moisture/1023)*100);

if(document.getElementById("moistureBar")){
document.getElementById("moistureBar").style.width=moisturePercent+"%";
}


/* irrigation advice */

irrigationAdvice(latest.moisture);


/* update chart */

updateChart(data);

})

.catch(err=>console.error("Sensor data error:",err));

}


/* =====================================
📊 UPDATE CHART
===================================== */

function updateChart(data){

const ctx=document.getElementById("sensorChart").getContext("2d");

let labels=data.map(d=>d.timestamp);
let moisture=data.map(d=>d.moisture);

if(chart) chart.destroy();

chart=new Chart(ctx,{
type:"line",
data:{
labels:labels,
datasets:[{
label:"Moisture",
data:moisture,
borderColor:"#2e7d32",
backgroundColor:"rgba(46,125,50,0.2)",
tension:0.4,
fill:true
}]
},
options:{
responsive:true,
maintainAspectRatio:false
}
});

}


/* =====================================
🔁 AUTO REFRESH
===================================== */

loadWeather();
loadData();

setInterval(loadWeather,60000);
setInterval(loadData,5000);