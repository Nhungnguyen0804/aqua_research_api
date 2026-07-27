from src.prompt import build_review_prompt
from src.services.llm import invoke_gemini
from src.schema import ReviewResult
from src.nodes.extract_node import analyze_one
from src.state import LitState
from src.utils import save_list_dict_to_csv

def review_one(paper: dict, max_retry: int = 2) -> dict:
    for attempt in range(max_retry + 1):
        messages = build_review_prompt(paper)
        try:
            review = invoke_gemini(messages, ReviewResult)
        except Exception as e:
            paper["review_status"] = "review_failed"
            paper["review_error"] = str(e)
            return paper

        if review.is_grounded:
            paper["review_status"] = "grounded"
            return paper

        # không grounded -> retry lại analyze_one, rồi review lại
        paper["review_issues"] = review.issues
        if attempt < max_retry:
            paper = analyze_one(paper)  # trích xuất lại
        else:
            paper["review_status"] = "ungrounded_after_retry"

    return paper


def reviewer_node(state: LitState) -> LitState:
    papers = state.get("included_papers", [])
    print(f"[reviewer] đang kiểm tra chính xác của extract từ {len(papers)} papers...")

    results = []
    for i, paper in enumerate(papers, 1):
        result = review_one(paper)
        results.append(result)
        if i % 5 == 0 or i == len(papers):
            print(f"  ...{i}/{len(papers)}")

    extract_true_count = 0
    for p in results:
        if p.get('review_status') == 'grounded': # là extract ra đúng 
            extract_true_count +=1

    print(f"[reviewer] xong. extract_true_count: {extract_true_count}, còn vấn đề: {len(results) - extract_true_count}")
    # topic_dir
    # topic_dir = 'data/topic_dir'
    # path = f'{topic_dir}/reviewed_papers.csv'
    # save_list_dict_to_csv(results, path)
    state["reviewed_papers"] = results
    return state