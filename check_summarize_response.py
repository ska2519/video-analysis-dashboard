from twelvelabs import TwelveLabs
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
VIDEO_ID = os.getenv("VIDEO_ID")
client = TwelveLabs(api_key=API_KEY)

print("Testing summarize...")
try:
    res = client.summarize(
        video_id=VIDEO_ID,
        type="summary",
        prompt="Describe the first 5 seconds."
    )
    print(f"Result Type: {type(res)}")
    print(f"Dir(res): {dir(res)}")
    if hasattr(res, 'summary'):
        print(f"Result Summary: {res.summary}")
    # Inspect other fields
except Exception as e:
    print(f"Error: {e}")
