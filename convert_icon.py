from PIL import Image
import os

try:
    img = Image.open("Niro_original.png")
    # Convert to RGBA to support transparency if not already
    img = img.convert("RGBA")
    # Save as ICO
    img.save("logo.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("Successfully converted Niro_original.png to logo.ico")
except Exception as e:
    print(f"Error converting icon: {e}")
