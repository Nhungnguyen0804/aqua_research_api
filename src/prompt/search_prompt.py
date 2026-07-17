from src.utils import get_current_time

def build_search_messages(query: str):
    return [
        {
            "role": "system",
            "content": "You are a research assistant. Bạn tên là LitResearcher."
        },
        {
            "role": "system",
            "content": f"Thông tin bổ sung: Current time: {get_current_time()}"
        },
        {
            "role": "user",
            "content": query
        }
    ]