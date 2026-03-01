const translations = {
    en: {
        live_status: "Live Field Status",
        moisture: "Moisture",
        temperature: "Temperature",
        humidity: "Humidity",
        crop_rec: "Crop Recommendation",
        soil: "Soil Condition",
        crop: "Recommended Crop",
        fertilizer: "Fertilizer",
        yield: "Yield Prediction",
        land: "Enter Land (in acres):",
        predict: "Predict"
    },

    hi: {
        live_status: "लाइव खेत स्थिति",
        moisture: "नमी",
        temperature: "तापमान",
        humidity: "आर्द्रता",
        crop_rec: "फसल सिफारिश",
        soil: "मिट्टी की स्थिति",
        crop: "सुझाई गई फसल",
        fertilizer: "उर्वरक",
        yield: "उपज पूर्वानुमान",
        land: "भूमि दर्ज करें (एकड़ में):",
        predict: "अनुमान करें"
    },

    te: {
        live_status: "ప్రస్తుత పొల స్థితి",
        moisture: "తేమ",
        temperature: "ఉష్ణోగ్రత",
        humidity: "ఆర్ద్రత",
        crop_rec: "పంట సిఫార్సు",
        soil: "మట్టి స్థితి",
        crop: "సిఫార్సు చేసిన పంట",
        fertilizer: "ఎరువు",
        yield: "పంట దిగుబడి అంచనా",
        land: "భూమి నమోదు చేయండి (ఎకరాల్లో):",
        predict: "అంచనా వేయండి"
    }
};

function changeLanguage(lang) {
    document.querySelectorAll("[data-key]").forEach(element => {
        const key = element.getAttribute("data-key");
        element.innerText = translations[lang][key];
    });
}