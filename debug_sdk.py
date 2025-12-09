from twelvelabs import TwelveLabs
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = TwelveLabs(api_key=API_KEY)

print(f"Type of client.generate: {type(client.generate)}")
print(f"Dir of client.generate: {dir(client.generate)}")
