import time
import wave
import sounddevice as sd
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont, ImageDraw

# Function to record audio and save it as a WAV file
def record_audio_to_file(filename="recording.wav", duration=5, samplerate=16000):
    try:
        # Display a message on the screen during recording
        display_message(device, "Recording audio...", font)
        
        print("Recording audio...")
        # Record audio from the microphone
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()  # Wait until the recording is finished
        print("Recording complete.")
        
        # Save the recording as a WAV file
        with wave.open(filename, 'w') as wf:
            wf.setnchannels(1)  # Mono audio
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(samplerate)
            wf.writeframes(audio_data.tobytes())
        
        print(f"File saved as {filename}")
        display_message(device, "Recording saved!", font)
        
        return filename
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)
        display_message(device, error_message, font)
        return None

# Function to display a message on the OLED screen
def display_message(device, message, font):
    with canvas(device) as draw:
        draw.text((5, 20), message, font=font, fill="white")

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
        display_message(device, "Ready to record", font)
    time.sleep(2)
    
    # Record audio and save it as a WAV file
    output_file = record_audio_to_file(duration=5)
    
    # Final message
    if device and output_file:
        display_message(device, "Done! File saved", font)
    time.sleep(5)
