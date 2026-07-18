from datetime import datetime
from src.state import LitState

MIN_YEAR = datetime.now().year - 10   # bỏ bài cũ hơn 10 năm
BATCH_SIZE = 10      # số bài gửi mỗi lần gọi API

def check_condition_year(paper: dict) -> bool:
    year = paper.get("year")
    if year is None:
        return False
    if year >= MIN_YEAR:
        return True



def filter_node(state:LitState) -> LitState:
    deduped_papers = state.get('deduped_papers')
    print('[filter] min year (hiện tại - 10 năm) = ', MIN_YEAR)
    
    filtered_papers = []
    for paper in deduped_papers:
        if check_condition_year(paper):
            filtered_papers.append(paper)
    
    print(f'[filter] số lượng paper lọc theo năm: {len(filtered_papers)}' )
    state['filtered_papers'] = filtered_papers
    return state