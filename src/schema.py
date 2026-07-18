from pydantic import BaseModel, Field

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