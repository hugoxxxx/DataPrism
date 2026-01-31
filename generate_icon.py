from PIL import Image
import os

if not os.path.exists('assets'):
    os.makedirs('assets')

img = Image.open('src/resources/app_icon.png')
# Save as ICO with multiple sizes for best Windows compatibility
img.save('assets/icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print("Converted app_icon.png to assets/icon.ico")
