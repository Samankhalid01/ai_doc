import requests
import sys

url = 'http://localhost:8000/process'
file_path = 'test.pdf'

try:
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'application/pdf')}
        resp = requests.post(url, files=files, timeout=30)
        print('Status code:', resp.status_code)
        try:
            print(resp.json())
        except Exception as e:
            print('Response text:', resp.text)
except Exception as e:
    print('Error:', e)
    sys.exit(1)
