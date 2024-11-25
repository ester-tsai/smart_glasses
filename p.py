import time
import requests
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageDraw, ImageFont

# Function to get text from an API
def fetch_text_from_api():
    try:
        response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
        if response.status_code == 200:
            data = response.json()
            print(data)
            print("Now sending to the screen")
            return data['title']  # Return the title of the post
        else:
            return "Failed to fetch data"
    except requests.RequestException as e:
        return f"Error: {str(e)}"

# Create serial interface, assuming default I2C address of 0x3C
serial = i2c(port=1, address=0x3C)

# Create device with SSD1306 driver
device = ssd1306(serial)

# Text to display
text = fetch_text_from_api()
font = ImageFont.load_default()

# Display text statically
def display_text(device, text, font):
    with canvas(device) as draw:
        draw.text((10, 20), text, font=font, fill="white")

# Run the display text function
display_text(device, text, font)

# Keep the display on
time.sleep(10)
