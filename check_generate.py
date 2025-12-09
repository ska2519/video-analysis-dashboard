from twelvelabs import TwelveLabs
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
VIDEO_ID = os.getenv("VIDEO_ID")
client = TwelveLabs(api_key=API_KEY)

print("Testing generate without start/end args, but in prompt...")
try:
    # Prompt with time
    prompt = "From 0s to 5s, describe the scene."
    
    res = client.generate(
        video_id=VIDEO_ID,
        prompt=prompt,
        stream=False
    )
    print(f"Result Type: {type(res)}")
    print(f"Dir(res): {dir(res)}")
    # Try to find the text
    if hasattr(res, 'data'):
        print(f"Result Data: {res.data}")
    if hasattr(res, 'text'):
        print(f"Result Text: {res.text}")
        
except Exception as e:
    print(f"Error: {e}")
