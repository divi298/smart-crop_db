from gtts import gTTS
import requests
import os

# 🔴 Replace with your values
BOT_TOKEN = "8425906172:AAG3ATWwizXuB9rcB9fFvBSg2YqJImPxZoM"
CHAT_ID = "8587788759"

# Example sensor data (you can replace with real values later)
temperature = 28
humidity = 75
crop = "బియ్యం"   # Rice in Telugu

# 🟢 Create Telugu voice message
message_text = f"""
ఈ రోజు ఉష్ణోగ్రత {temperature} డిగ్రీలు.
తేమ శాతం {humidity}.
సూచించిన పంట {crop}.
"""

# Generate voice file
tts = gTTS(text=message_text, lang="te")
audio_file = "crop_update.mp3"
tts.save(audio_file)

print("Voice file created successfully!")

# Send voice message to Telegram
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"

with open(audio_file, "rb") as audio:
    response = requests.post(
        url,
        data={"chat_id": CHAT_ID},
        files={"audio": audio}
    )

if response.status_code == 200:
    print("Voice message sent to Telegram successfully!")
else:
    print("Failed to send message:", response.text)

# Optional: remove file after sending
os.remove(audio_file)