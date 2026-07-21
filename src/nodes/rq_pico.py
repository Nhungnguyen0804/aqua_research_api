from src.state import LitState
from src.prompt import build_rq_rico_prompt
from src.services.llm import invoke_gemini
from src.schema import PICO
def rq_pico_node(state: LitState) -> LitState:
    mess = build_rq_rico_prompt(state['topic'])
    pico = invoke_gemini(mess, PICO)
    # print(f'[pico] = {pico}')
    print('---------------------------------------------------------------')
    print(f'- Population: {pico.population}')
    print(f'- Intervention: {pico.intervention}')
    print(f'- Comparison: {pico.comparison}')
    print(f'- Outcome: {pico.outcome}')
    print(f'==> research question: {pico.research_question}')
    print('---------------------------------------------------------------')
    state['pico'] = pico
    return state 


# # test 
# print('test ===============================================')
# state = {
#         "topic": "Retrieval Augmented Generation",
#         'pico': None,
#     }

# print(rq_pico_node(state))