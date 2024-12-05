import os
import wave
import subprocess
import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont
import pyaudio

# Constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100  # Microphone sampling rate
TARGET_RATE = 16000  # Whisper requires 16 kHz
TEMP_AUDIO_FILE = "temp_audio.wav"

# OLED setup
i2c = busio.I2C(board.SCL, board.SDA)
oled = SSD1306_I2C(128, 64, i2c)
font = ImageFont.load_default()

def write_to_oled(text):
    """
    Writes the text to the OLED display. Wraps text if it exceeds the screen width.
    """
    oled.fill(0)
    image = Image.new("1", (oled.width, oled.height))  # Create a new blank image
    draw = ImageDraw.Draw(image)

    # Word wrap
    words = text.split(" ")
    lines = []
    line = ""
    for word in words:
        if len(line) + len(word) + 1 <= 16:  # Adjust character limit for each line
            line += word + " "
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())

    # Draw each line
    y = 0
    for line in lines:
        draw.text((0, y), line, font=font, fill=255)
        y += 10  # Adjust line height as needed

    # Display the text
    oled.image(image)
    oled.show()

def transcribe_audio(file_path):
    """
    Transcribes audio using the Whisper model via the whisper command.
    """
    try:
        result = subprocess.run(
            ["whisper", "-m", "/usr/local/share/whisper/models/ggml-tiny.bin", "-f", file_path, "--translate"],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception as e:
        print("Error during transcription:", e)
        return "[ERROR]"

def record_audio():
    """
    Records audio for 5 seconds and saves it as a WAV file.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("Recording for 5 seconds...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * 5)):  # Record for 5 seconds
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
        except OSError as e:
            print(f"Audio read error: {e}")
            continue

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the audio to a file
    wf = wave.open(TEMP_AUDIO_FILE, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Convert to 16 kHz
    print("Resampling audio to 16 kHz...")
    resampled_file = "temp_resampled.wav"
    subprocess.run(
        ["ffmpeg", "-i", TEMP_AUDIO_FILE, "-ar", str(TARGET_RATE), "-ac", "1", resampled_file, "-y"],
        capture_output=True
    )
    return resampled_file

def main():
    """
    Main function to record, transcribe, and display transcription on the OLED.
    """
    try:
        audio_file = record_audio()
        transcription = transcribe_audio(audio_file)
        print("Transcription:", transcription)
        write_to_oled(transcription)
    finally:
        if os.path.exists(TEMP_AUDIO_FILE):
            os.remove(TEMP_AUDIO_FILE)
        if os.path.exists("temp_resampled.wav"):
            os.remove("temp_resampled.wav")

if __name__ == "__main__":
    main()
