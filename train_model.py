import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Create simple demo dataset
data = {
    "soil": [1, 1, 0, 0, 1, 0, 1, 0],
    "temperature": [30, 28, 35, 33, 26, 38, 29, 31],
    "humidity": [80, 75, 40, 35, 70, 30, 85, 45],
    "crop": ["Rice", "Rice", "Millet", "Millet", "Rice", "Millet", "Rice", "Millet"]
}

df = pd.DataFrame(data)

X = df[["soil", "temperature", "humidity"]]
y = df["crop"]

le = LabelEncoder()
y_encoded = le.fit_transform(y)

model = RandomForestClassifier()
model.fit(X, y_encoded)

# Save model and encoder
joblib.dump(model, "crop_model.pkl")
joblib.dump(le, "label_encoder.pkl")

print("Model trained and saved successfully!")