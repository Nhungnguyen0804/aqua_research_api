from src.state import LitState
from datetime import date

def paper_line(p: dict) -> str:
    title = p.get("title", "Untitled")
    year = p.get("year", "n/a")
    doi = p.get("doi")
    link = f"https://doi.org/{doi}" if doi else p.get("url", "")
    finding = p.get("key_findings", "")
    return f"- **{title}** ({year}) — {finding}  \n  [{link}]({link})"

def report_node(state: LitState) -> LitState:
    topic = state.get("topic", "")
    pico = state.get("pico")
    synthesis = state.get("synthesis", {})
    reviewed = state.get("reviewed_papers", [])
    good_papers = [p for p in reviewed if p.get("review_status") == "grounded"]

    md = []
    md.append(f"# Literature Review: {topic}")
    md.append(f"*Ngày tạo: {date.today().isoformat()}*\n")

    md.append("## 1. Giới thiệu")
    if pico:
        md.append(f"- **Population**: {pico.population}")
        md.append(f"- **Intervention**: {pico.intervention}")
        md.append(f"- **Comparison**: {pico.comparison}")
        md.append(f"- **Outcome**: {pico.outcome}\n")

    md.append("## 2. Phương pháp tìm kiếm")
    md.append(f"| Bước | Số lượng |")
    md.append(f"|---|---|")
    md.append(f"| Raw papers | {len(state.get('raw_papers', []))} |")
    md.append(f"| Sau dedup | {len(state.get('deduped_papers', []))} |")
    md.append(f"| Sau screening | {len(state.get('screened_papers', []))} |")
    md.append(f"| Đủ tiêu chí (eligible) | {len(state.get('eligible_papers', []))} |")
    md.append(f"| Included (đã extract) | {len(state.get('included_papers', []))} |")
    md.append(f"| Reviewed đạt (grounded) | {len(good_papers)} |\n")

    md.append("## 3. Tổng hợp kết quả")
    md.append(synthesis.get("overall_summary", "(chưa có)") + "\n")

    md.append("### Các hướng tiếp cận chính")
    for t in synthesis.get("themes", []):
        md.append(f"**{t['theme_name']}**  ")
        md.append(f"{t['description']}  ")
        md.append(f"*Papers liên quan: {', '.join(t['papers'])}*\n")

    md.append("## 4. Research Gaps")
    for g in synthesis.get("gaps", []):
        md.append(f"- {g['gap_description']}  ")
        md.append(f"  *(dựa trên: {', '.join(g['supporting_papers'])})*")
    md.append("")

    md.append("## 5. Danh sách paper đã đưa vào review")
    for p in good_papers:
        md.append(paper_line(p))
    md.append("")

    md.append("## 6. Kết luận & đề xuất")
    md.append(synthesis.get("recommendations", "(chưa có)"))

    report_text = "\n".join(md)
    path = "data/topic_dir/report.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"[report] đã xuất báo cáo -> {path}")
    state["report_content"] = report_text
    return state
