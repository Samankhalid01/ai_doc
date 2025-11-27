from PIL import Image, ImageDraw, ImageFont
import requests
import io

url = 'http://localhost:8000/process'

# Create a simple test image
img = Image.new('RGB', (800, 400), color=(255, 255, 255))
draw = ImageDraw.Draw(img)
draw.text((20, 20), "Invoice\nInvoice Number: 6312\nTotal: $58658.00\nDate: 11/15/2025", fill=(0, 0, 0))

buf = io.BytesIO()
img.save(buf, format='JPEG')
buf.seek(0)

files = {'file': ('test.jpg', buf, 'image/jpeg')}

try:
    resp = requests.post(url, files=files, timeout=60)
    print('Status code:', resp.status_code)
    try:
        print(resp.json())
    except Exception:
        print('Response text:', resp.text)
except Exception as e:
    print('Error:', e)
    raise
