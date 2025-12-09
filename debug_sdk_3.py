from twelvelabs import TwelveLabs
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = TwelveLabs(api_key=API_KEY)

help(client.summarize)
