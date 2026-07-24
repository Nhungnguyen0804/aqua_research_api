from pydantic import BaseModel, Field # định nghĩa cấu trúc dữ liệu (schema) bằng class.

# BaseModel (Pydantic) = cái mà mình muốn LLM trả về trông như thế nào 
# field tạo json schema cho gemini biet  , gom type va mota trong json đó giúp model hiểu rõ hơn 
class PICO(BaseModel):
    population: str = Field(description="Đối tượng nghiên cứu, VD: chemical compounds/drugs in discovery phase")
    intervention: str = Field(description="Phương pháp/công nghệ chính, VD: deep learning models")
    comparison: str = Field(description="Phương pháp đối chứng, VD: traditional ML (SVM, RF, XGBoost), QSAR, docking")
    outcome: str = Field(description="Kết quả đo lường, VD: toxicity prediction performance (AUC-ROC, F1...)")
    research_question: str = Field(description="1 câu RQ tổng hợp từ 4 thành phần trên")

class StringList(BaseModel):
    string_list: list[str]

class PaperRelevance(BaseModel):
    id: str
    relevant: bool
    reason: str

class FilterResult(BaseModel):
    results: list[PaperRelevance]

class EligibilityCriteria(BaseModel):
    inclusion_criteria: list[str]
    exclusion_criteria: list[str]

class PaperAnalysis(BaseModel):
    contribution: str = Field(description="Đóng góp chính của bài báo")
    method: str = Field(description="Phương pháp/kỹ thuật chính được sử dụng")
    limitation: str = Field(description="Hạn chế được tác giả nêu ra hoặc suy ra được")
    key_findings: str = Field(description="Kết quả/phát hiện chính")

class ReviewResult(BaseModel):
    is_grounded: bool = Field(description="True nếu extracted info được source text hỗ trợ")
    issues: str = Field(default="", description="Mô tả các mục không có căn cứ, nếu có")


class ThemeGroup(BaseModel):
    theme_name: str
    description: str
    papers: list[str] 

class ResearchGap(BaseModel):
    gap_description: str
    supporting_papers: list[str] # paper cho thấy gap này 

class SynthesisResult(BaseModel):
    overall_summary: str
    themes: list[ThemeGroup]
    gaps: list[ResearchGap]
    recommendations: str