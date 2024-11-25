import time
import speech_recognition as sr
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont, ImageDraw
print(sr.Microphone.list_microphone_names())
# Function to display a message on the OLED screen
def display_message(device, message, font):
    with canvas(device) as draw:
        draw.text((5, 20), message, font=font, fill="white")

# Speech recognition function for a 5-second recording
def transcribe_audio(duration=5):
    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=0)
    while True:
        with mic as source:
            # Capture small chunks of speech continuously
            print("Recording...")
            audio = recognizer.listen(source, timeout=100, phrase_time_limit=duration)
            print("Recording stopped")
            try:
                # Transcribe the audio chunk immediately
                text = recognizer.recognize_google(audio)
                print(f"Recognized: {text}")
            except sr.UnknownValueError:
                print("...")  # Display silence if nothing is understood
            except sr.RequestError as e:
                print(f"API error: {e}")

# Setup for the OLED screen (SSD1306)
try:
    # Create I2C interface for OLED
    serial = i2c(port=1, address=0x3C)
    device = ssd1306(serial)
    font = ImageFont.load_default()
except Exception as e:
    print(f"Error initializing OLED: {str(e)}")
    device = None

# Main logic
if __name__ == "__main__":
    # Display initial message on the OLED
    if device:
        display_message(device, "Ready to transcribe", font)
    time.sleep(2)

    # Start listening for speech and transcribing
    try:
        transcribe_audio(duration=5)
    except KeyboardInterrupt:
        print("Stopped by user.")
