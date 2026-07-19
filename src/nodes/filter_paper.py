from datetime import datetime
import math
from src.state import LitState
from src.prompt import build_filter_prompt
from src.services.llm import invoke_gemini
from src.schema import PaperRelevance,FilterResult
from copy import deepcopy
SKIP_YEAR = 5
MIN_YEAR = datetime.now().year - SKIP_YEAR  # bỏ bài cũ hơn 10 năm
BATCH_SIZE = 10      # số bài gửi mỗi lần gọi API

def check_condition_year(paper: dict) -> bool:
    year = paper.get("year")
    if year is None:
        return False
    if year >= MIN_YEAR:
        return True



def filter_node(state:LitState) -> LitState:
    deduped_papers = state.get('deduped_papers')
    print(f'[filter] min year (hiện tại - {SKIP_YEAR} năm) = ', MIN_YEAR)
    
    year_filtered = []
    for paper in deduped_papers:
        if check_condition_year(paper):
            year_filtered.append(paper)
    
    print(f'[filter] số lượng paper lọc theo năm: {len(year_filtered)}' )

    pico = state.get('research_question')
    print(f'[filter] pico = {pico}')
    filtered_papers =[]

    num_batches = math.ceil(len(year_filtered) / BATCH_SIZE) # làm tròn lên số nguyên gần nhất 
    for num_batch in range(num_batches):
        start = num_batch * BATCH_SIZE
        end = start + BATCH_SIZE

        batch = year_filtered[start:end]
        print(f'[filter] xử lý batch {num_batch + 1}/{num_batches} ({len(batch)} bài)')

        mess = build_filter_prompt(pico, year_filtered)
        response = invoke_gemini(mess, FilterResult)

        for item in response.results:
            idx = int(item.id)  # str-> int 
            if item.relevant == True: 
                paper = deepcopy(year_filtered[idx])
                paper['reason'] = item.reason 
                filtered_papers.append(paper)
    print(f'[filter] số lượng paper sau khi lọc PICO: {len(filtered_papers)}')
    state['filtered_papers'] = filtered_papers
    return state



# Ví dụ BATCH_SIZE = 10:

# b = 0 → start_index = 0, end_index = 10
# b = 1 → start_index = 10, end_index = 20
# b = 2 → start_index = 20, end_index = 30