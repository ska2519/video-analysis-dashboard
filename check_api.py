import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
VIDEO_ID = os.getenv("VIDEO_ID")

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "video_id": VIDEO_ID,
    "prompt": "Describe this",
    "stream": False
}

urls = [
    "https://api.twelvelabs.io/v1.1/generate",
    "https://api.twelvelabs.io/v1.2/generate",
    "https://api.twelvelabs.io/v1.3/generate",
    "https://api.twelvelabs.io/v1.1/pegasus/generate",
    "https://api.twelvelabs.io/v1.2/pegasus/generate",
]

for url in urls:
    print(f"Testing {url}...")
    try:
        res = requests.post(url, headers=headers, json=payload)
        print(f"Status: {res.status_code}")
        if res.status_code != 404:
            print(f"Found! {res.text}")
    except Exception as e:
        print(f"Error: {e}")
