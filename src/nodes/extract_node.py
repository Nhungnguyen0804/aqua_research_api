import fitz  # PyMuPDF
import os 
import requests 
from src.state import LitState
from src.schema import PaperAnalysis
from src.prompt import build_extract_prompt
from src.services.llm import invoke_gemini 
from src.utils import save_list_dict_to_csv

import random
PDF_DIR = "data/pdfs"
os.makedirs(PDF_DIR, exist_ok=True)
def safe_filename(paper: str) -> str:
    # paper_id = paper.get('paper_id')
    num = random.random()
    return f"{num}.pdf"


def download_pdf(pdf_url: str, pdf_dir: str,  paper: dict, timeout: int = 20) -> str | None:
    if not pdf_url:
        return None
    path = os.path.join(pdf_dir, safe_filename(paper))
    try:
        headers = {"User-Agent": "Mozilla/5.0 (LitResearcher/1.0)"}
        resp = requests.get(pdf_url, headers=headers, timeout=timeout, stream=True)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")
        if "pdf" not in content_type.lower() and not pdf_url.lower().endswith(".pdf"):
            return None
        
        with open(path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return path
    except Exception as e :
        print(f"[fulltext][bug] {paper.get('paper_id')}: LỖI {type(e).__name__}: {e}")
        return None
    

def extract_text_from_pdf(path: str, max_pages: int = 40) -> str | None:
    try:
        doc = fitz.open(path)
        text = []

        for i, page in enumerate(doc):
            if i < max_pages:
                text.append(page.get_text())

        doc.close()
        full_text = "\n".join(text).strip()
        return full_text if len(full_text) > 200 else None
    except Exception:
        return None
    
def process_one(paper: dict , pdf_dir) -> dict:
    """Tải + extract + xóa file ngay, chỉ giữ text lại."""
    pdf_url = paper.get("pdf_url") or paper.get("url")
    path = download_pdf(pdf_url, pdf_dir,  paper)

    if path:
        text = extract_text_from_pdf(path)
        # os.remove(path)  # xóa ngay 
        if text:
            paper["full_text"] = text
            paper["full_text_source"] = "pdf"
            return paper

    paper["full_text"] = paper.get("abstract")
    paper["full_text_source"] = "abstract_only"
    return paper

def analyze_one(paper: dict) -> dict:
    try:
        messages = build_extract_prompt(paper)
        result = invoke_gemini(messages, PaperAnalysis)
        paper["contribution"] = result.contribution
        paper["method"] = result.method
        paper["limitation"] = result.limitation
        paper["key_findings"] = result.key_findings
        paper["analysis_status"] = "ok"
    except Exception as e:
        paper.setdefault("contribution", "")
        paper.setdefault("method", "")
        paper.setdefault("limitation", "")
        paper.setdefault("key_findings", "")
        paper["analysis_status"] = "failed"
        paper["analysis_error"] = f"{type(e).__name__}: {e}"
    return paper


def process_and_analyze(paper: dict , pdf_dir) -> dict:
    paper = process_one(paper , pdf_dir) # thêm trường full text 
    paper = analyze_one(paper)
    return paper 


def normalize_text(text):
    text = text.replace(' ', '_')
    return text 
# fulltext
def extract_node(state: LitState) -> LitState:
    topic = state.get('topic')
    topic_name_dir = normalize_text(topic)
    PDF_TOPIC_DIR = f'{PDF_DIR}/{topic_name_dir}'
    os.makedirs(PDF_TOPIC_DIR, exist_ok=True)
    eli_papers = state.get("eligible_papers", [])
    results = []
    for i, paper in enumerate(eli_papers, 1):
        result = process_and_analyze(paper , PDF_TOPIC_DIR)
        results.append(result)
        if i % 5 == 0 or i == len(eli_papers):
            print(f"  ...{i}/{len(eli_papers)}")


    success = 0
    for p in results:
        if p["full_text_source"] == "pdf":
            success += 1
    
    success_analysis = 0
    for p in results:
        if p.get("analysis_status") == "ok":
            success_analysis +=1 
    print(f"[fulltext] xong. thành công pdf: {success}, chỉ có abstract: {len(results) - success}")
    print(f"[fulltext] xong. thành công success_analysis: {success_analysis}, chỉ có abstract: {len(results) - success_analysis}")
    # topic_dir
    topic_dir = 'data/topic_dir'
    path = f'{topic_dir}/included_papers.csv'
    save_list_dict_to_csv(results, path)
   
   
    state["included_papers"] = results
    return state