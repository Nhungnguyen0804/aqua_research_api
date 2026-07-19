from src.state import LitState
from src.services.llm import invoke_gemini
from src.prompt import build_eligibility_criteria_prompt,build_eligibility_prompt
from src.schema import EligibilityCriteria, FilterResult
import math
from copy import deepcopy
def criteria_node(state: LitState) -> LitState:
    pico = state.get('pico')
    rq = pico.research_question if hasattr(pico, 'research_question') else state.get('research_question')

    messages = build_eligibility_criteria_prompt(pico, rq)
    criteria = invoke_gemini(messages, EligibilityCriteria)

    print(f'[criteria] inclusion: {criteria.inclusion_criteria}')
    print(f'[criteria] exclusion: {criteria.exclusion_criteria}')

    state['eligibility_criteria'] = criteria
    return state


BATCH_SIZE = 20

def eligibility_node(state: LitState) -> LitState:
    screened_papers = state.get('screened_papers')
    eligibility_criteria = state.get('eligibility_criteria')
    eligible_papers = []
    num_batches = math.ceil(len(screened_papers) / BATCH_SIZE) # làm tròn lên số nguyên gần nhất 
    for num_batch in range(num_batches):
        start = num_batch * BATCH_SIZE
        end = start + BATCH_SIZE
        batch = screened_papers[start:end]
        print(f'[eligibility] xử lý batch {num_batch + 1}/{num_batches} ({len(batch)} bài)')
        mess = build_eligibility_prompt(eligibility_criteria, batch)
        response = invoke_gemini(mess, FilterResult)
        for item in response.results:
                idx = int(item.id)
                if item.relevant == True:
                    paper = deepcopy(batch[idx]) 
                    paper['eligibility_reason'] = item.reason
                    eligible_papers.append(paper)

    print(f'[eligibility] số lượng paper sau Eligibility: {len(eligible_papers)}')
    state['eligible_papers'] = eligible_papers
    return state