from sentence_transformers import SentenceTransformer, util

emb_model = None # nội bộ, embedding model


def get_embedding_model() -> SentenceTransformer:
    """Load model 1 lần, cache lại"""
    global emb_model
    if emb_model is None:
        emb_model = SentenceTransformer('all-MiniLM-L6-v2')
    return emb_model


def embed_text_list(texts: list[str]):
    """Encode 1 list text thành tensor embeddings"""
    model = get_embedding_model()
    return model.encode(texts, convert_to_tensor=True)

def embed_text(text: str):
    """Encode 1 text đơn thành embedding."""
    model = get_embedding_model()
    return model.encode(text, convert_to_tensor=True)

def compute_similarity(query_embedding, candidate_embeddings) -> list[float]:
    """Cosine similarity giữa 1 embedding query và nhiều embedding candidate."""
    scores = util.cos_sim(query_embedding, candidate_embeddings)[0] # ma trận [[...]], [0] lấy hàng đầu tiên là [...], chỉ có 1 query => chỉ có [0] , 2 query là [0] [1]
    return scores.tolist()