import os
try:
    from llama_cpp import Llama
    _LLAMA_AVAILABLE = True
except Exception:
    Llama = None
    _LLAMA_AVAILABLE = False


class ModelLoader:
    def __init__(self):
        self.model_path = os.getenv("MODEL_PATH", "./models/model.stub")
        self.threads = int(os.getenv("LLAMA_THREADS", "4"))
        self.model = None
        self.loaded = False
        if _LLAMA_AVAILABLE and os.path.exists(self.model_path):
            try:
                self.model = Llama(model_path=self.model_path, n_threads=self.threads)
                self.loaded = True
            except Exception:
                self.loaded = False

    def answer(self, question, docs):
        """Return an answer string. If local llama is available and loaded, use it; otherwise return a dummy."""
        if not self.loaded:
            return "Dummy answer (no local LLM available)."

        # assemble context from docs (simple concatenation, truncated)
        parts = []
        for d in docs[:5]:
            t = d.get("text", "")
            parts.append(t[:2000])
        context = "\n\n".join(parts)
        prompt = (
            "Use the following context to answer the question. Cite sources when possible.\n\n"
            f"CONTEXT:\n{context}\n\nQUESTION: {question}\n\nAnswer concisely."
        )

        try:
            resp = self.model.create(prompt=prompt, max_tokens=256, temperature=0.2)
            # llama-cpp-python may return choices
            if isinstance(resp, dict) and resp.get("choices"):
                text = resp["choices"][0].get("text") or resp["choices"][0].get("message", {}).get("content")
                return text if text is not None else str(resp)
            return str(resp)
        except Exception:
            return "Model inference failed."
