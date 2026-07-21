from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import API_KEYS
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

import time
current_key = 0
LLM_cache = {}  # cache instance theo key index

def get_llm(key_idx: int) -> ChatGoogleGenerativeAI:
    if key_idx not in LLM_cache:
        LLM_cache[key_idx] = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=API_KEYS[key_idx],
        )
    return LLM_cache[key_idx]

def is_quota_error(e: Exception) -> bool:
    msg = str(e)
    return "RESOURCE_EXHAUSTED" in msg or "429" in msg

def is_auth_error(e: Exception) -> bool:
    msg = str(e)
    return (
        "UNAUTHENTICATED" in msg
        or "401" in msg
        or "ACCESS_TOKEN_TYPE_UNSUPPORTED" in msg
        or "invalid authentication credentials" in msg.lower()
    )

def invoke_gemini(prompt , output_schema=None,  max_retries_per_key: int = 3) :
    global current_key

    while current_key < len(API_KEYS):
        llm = get_llm(current_key)

        if output_schema:
            llm = llm.with_structured_output(output_schema)
        for retry in range(max_retries_per_key):
            try:
                return llm.invoke(prompt)

            except ChatGoogleGenerativeAIError as e:
                if is_quota_error(e):
                    print(f"Key {current_key + 1} hết quota, chuyển key...")
                    current_key += 1
                    break  # thoát vòng retry, sang key mới
                if is_auth_error(e):
                    print(f"API key {current_key} bị lỗi xác thực -> bỏ key này")
                    current_key += 1
                    break 
                else:
                    wait = 2 ** retry
                    print(f"Lỗi tạm thời: {e} -> đợi {wait}s rồi thử lại")
                    time.sleep(wait)
                    if retry == max_retries_per_key - 1:
                        raise
            except Exception as e:
                print(f"Lỗi không liên quan quota: {e}")
                print(f"DEBUG type: {type(e)}")
                # lỗi không phải quota
                wait = 2 ** retry
                print(f"Lỗi tạm thời: {e} -> đợi {wait}s rồi thử lại")
                time.sleep(wait)
                if retry == max_retries_per_key - 1:
                    raise

    raise Exception("Tất cả API Key đều đã hết quota.")