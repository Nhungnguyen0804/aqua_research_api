from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import API_KEYS

current_key = 0


def invoke_gemini(prompt) :
    global current_key

    while current_key < len(API_KEYS):

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=API_KEYS[current_key],
        )

        try:
            return llm.invoke(prompt)

        except Exception as e:
            print(f"Key {current_key + 1} lỗi, chuyển sang key tiếp theo...")

            current_key += 1

    raise Exception("Tất cả API Key đều đã hết quota.")