from datetime import datetime
from typing import List
import json
import pandas as pd 
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

def save_list_dict_to_csv(listDict : List[dict] , path_csv : str):
    df = pd.DataFrame(listDict)
    df.to_csv(path_csv, index=False, encoding="utf-8-sig")

