import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the OLED display (128x64 resolution)
oled = SSD1306_I2C(128, 64, i2c)

# Clear the display
oled.fill(0)
oled.show()

# Create a blank image for drawing
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

# Draw a rectangle
draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=0)

# Add text
font = ImageFont.load_default()
draw.text((10, 10), "Hello, OLED!", font=font, fill=255)

# Display image on the OLED
oled.image(image)
oled.show()
