import os
import json
import math

_embed_model_instance = None

def get_embed_model():
    global _embed_model_instance
    if _embed_model_instance is not None:
        return _embed_model_instance
    
    try:
        from sentence_transformers import SentenceTransformer
        _embed_model_instance = SentenceTransformer('all-MiniLM-L6-v2')
        return _embed_model_instance
    except Exception as e:
        print(f"Warning: Could not load sentence-transformers: {e}")
        return None


class Retriever:
    def __init__(self):
        self.index_path = os.getenv("INDEX_PATH", "./data/index.json")
        self.emb_path = os.path.join(os.path.dirname(__file__), "..", "data", "embeddings.json")
        self.indexed = bool(os.path.exists(self.index_path) and os.path.exists(self.emb_path))

    def _cosine(self, a, b):
        try:
            dot = sum(x * y for x, y in zip(a, b))
            na = math.sqrt(sum(x * x for x in a))
            nb = math.sqrt(sum(y * y for y in b))
            if na == 0 or nb == 0:
                return 0.0
            return dot / (na * nb)
        except Exception:
            return 0.0

    def _embed_query(self, q):
        model = get_embed_model()
        if model:
            try:
                return model.encode(q).tolist()
            except Exception:
                pass
        return [1.0] * 8

    def retrieve(self, query, k=3):
        if not self.indexed:
            return [{"id": "sample", "text": "Sample document. Enable real retrieval by uploading documents."}]

        try:
            with open(self.emb_path, 'r', encoding='utf-8') as f:
                embeddings = json.load(f)
        except Exception:
            return [{"id": "emb_error", "text": "Failed to read embeddings."}]

        qv = self._embed_query(query)
        scores = []
        for chunk_id, vec in embeddings.items():
            score = self._cosine(qv, vec)
            scores.append((chunk_id, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        
        # Load index to map chunk_id to filename
        index_path = os.getenv("INDEX_PATH", "./data/index.json")
        index_data = {}
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        except Exception:
            pass
        
        for chunk_id, score in scores[:k]:
            # Extract filename from chunk_id (format: filename_chunk_N)
            parts = chunk_id.rsplit('_chunk_', 1)
            filename = parts[0] if parts else chunk_id
            
            doc_path = os.path.join(os.path.dirname(__file__), "..", "data", "docs", filename)
            text = ""
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except Exception:
                text = "(failed to read doc)"
            results.append({"id": chunk_id, "filename": filename, "score": float(score), "text": text[:2000]})
        return results
