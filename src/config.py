from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MY_GMAIL = os.getenv('MY_GMAIL','abc@example.com')
CORE_API_KEY = os.getenv('CORE_API_KEY', 'get_core_api')

index = 1
API_KEYS = []

while True:
    key = os.getenv(f"G_KEY_{index}")
    if key is None:
        break
    API_KEYS.append(key)
    index += 1

# print("Đã load", len(API_KEYS), "key")