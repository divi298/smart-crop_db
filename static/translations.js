const translations = {
    en: {
        moisture: "Moisture",
        temperature: "Temperature",
        humidity: "Humidity",
        recommendation: "Crop Recommendation",
        soil: "Soil",
        crop: "Crop",
        fertilizer: "Fertilizer"
    },
    te: {
        moisture: "తేమ",
        temperature: "ఉష్ణోగ్రత",
        humidity: "ఆర్ద్రత",
        recommendation: "పంట సిఫార్సు",
        soil: "మట్టి పరిస్థితి",
        crop: "పంట",
        fertilizer: "ఎరువు"
    },
    hi: {
        moisture: "नमी",
        temperature: "तापमान",
        humidity: "आर्द्रता",
        recommendation: "फसल सिफारिश",
        soil: "मिट्टी की स्थिति",
        crop: "फसल",
        fertilizer: "उर्वरक"
    }
};

document.getElementById("languageSwitcher").addEventListener("change", function() {
    let lang = this.value;

    document.querySelectorAll("[data-key]").forEach(el => {
        el.innerText = translations[lang][el.dataset.key];
    });
});