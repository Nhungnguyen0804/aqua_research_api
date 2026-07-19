from src.state import LitState
from src.prompt import build_rq_rico_prompt
from src.services.llm import invoke_gemini
from src.schema import PICO
def rq_pico_node(state: LitState) -> LitState:
    mess = build_rq_rico_prompt(state['topic'])
    pico = invoke_gemini(mess, PICO)
    print(f'[pico] = {pico}')
    state['pico'] = pico
    return state 
