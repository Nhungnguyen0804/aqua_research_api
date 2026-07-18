import json
from src.services.llm import invoke_gemini
from src.prompt import build_query_expansion_prompt
from src.schema import StringList

def query_expansion_node(state):
    messages = build_query_expansion_prompt(state["topic"])
    
    response = invoke_gemini(messages, StringList)
    sub_queries = response.string_list
    print(f'[sub_queries] = {sub_queries}')

    return {"sub_queries": sub_queries}