from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import GOOGLE_API_KEY, GEMINI_MODEL, TEMPERATURE

llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    temperature=TEMPERATURE,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    google_api_key=GOOGLE_API_KEY,
)

