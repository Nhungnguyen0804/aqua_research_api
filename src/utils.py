from datetime import datetime
import json

def get_current_time():
    return datetime.now().strftime("%H:%M:%S %d/%m/%Y")

def parse_json_response(text: str):
    text = (
        text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )
    return text