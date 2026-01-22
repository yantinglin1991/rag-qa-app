from fastapi import FastAPI, Request
from .model_loader import ModelLoader
from .retriever import Retriever
import os, time

app = FastAPI()
model = ModelLoader()
retriever = Retriever()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/qa")
async def qa(req: Request):
    body = await req.json()
    question = body.get("question")
    top_k = int(body.get("top_k", 3))
    if not question:
        return {"error": "missing question"}

    t0 = time.perf_counter()
    sources = retriever.retrieve(question, k=top_k)
    t_retrieval = (time.perf_counter() - t0) * 1000.0

    # RAG answer (with sources)
    t1 = time.perf_counter()
    rag_answer = model.answer(question, sources)
    t_llm_rag = (time.perf_counter() - t1) * 1000.0

    # Baseline answer (LLM-only)
    t2 = time.perf_counter()
    baseline_answer = model.answer(question, [])
    t_llm_baseline = (time.perf_counter() - t2) * 1000.0

    return {
        "question": question,
        "rag_answer": rag_answer,
        "baseline_answer": baseline_answer,
        "sources": sources,
        "timings": {
            "retrieval_ms": round(t_retrieval, 2),
            "llm_rag_ms": round(t_llm_rag, 2),
            "llm_baseline_ms": round(t_llm_baseline, 2),
        },
    }
