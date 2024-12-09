import asyncio
import nest_asyncio
import fastapi_poe as fp
from flask import Flask, request, jsonify
import os
import wave
import subprocess
import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont
import pyaudio

# Initialize Flask app
app = Flask(__name__)

# Constants for POE API
POE_API_KEY = "2-j_yibA8pbfozuVugcd8qTYAC-4Iu4XHNEOtuEV5qE"
nest_asyncio.apply()  # Allow nested event loops.

# Constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
TARGET_RATE = 16000
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
        if len(line) + len(word) + 1 <= 26:  # Adjust character limit for each line
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

def transcribe_audio(file_path):
    """
    Transcribes audio using Whisper (or another tool if available).
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

async def get_llm_response(prompt):
    """
    Send the prompt to the Poe language model and get the response.
    """
    message = fp.ProtocolMessage(role="user", content=prompt)
    full_response = ""
    async for partial in fp.get_bot_response(
        messages=[message], bot_name="GPT-4o-Mini", api_key=POE_API_KEY
    ):
        full_response += partial.text
    return full_response

@app.route("/record_and_chatgpt", methods=["POST"])
def record_and_chatgpt():
    """
    Records audio for 5 seconds, transcribes it, sends it to GPT via Poe API,
    and displays the response on the OLED.
    """
    try:
        # Step 1: Record audio and transcribe
        audio_file = record_audio()
        transcription = transcribe_audio(audio_file)
        print("Transcription:", transcription)

        # Extract text-only portion
        lines = transcription.split("\n")
        text_only = " ".join([line.split("]")[1].strip() for line in lines if "]" in line])

        # Step 2: Send to Poe API
        print("Sending to Poe GPT:", text_only)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        chatgpt_response = loop.run_until_complete(get_llm_response(text_only))
        print("Poe GPT Response:", chatgpt_response)

        # Step 3: Display response on OLED
        write_to_oled(chatgpt_response)

        # Respond to client
        response = {"status": "success", "transcription": text_only, "chatgpt_response": chatgpt_response}
    except Exception as e:
        print("Error:", e)
        response = {"status": "error", "message": str(e)}
    finally:
        if os.path.exists(TEMP_AUDIO_FILE):
            os.remove(TEMP_AUDIO_FILE)
        if os.path.exists("temp_resampled.wav"):
            os.remove("temp_resampled.wav")

    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
