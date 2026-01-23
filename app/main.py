from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from .model_loader import ModelLoader
from .retriever import Retriever
import time

app = FastAPI()
model = ModelLoader()
retriever = Retriever()

# Serve static files
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, '..', 'static')
if os.path.exists(static_dir):
    app.mount('/static', StaticFiles(directory=static_dir), name='static')


@app.get('/')
async def root():
    return FileResponse(os.path.join(static_dir, 'index.html'))


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.post('/qa')
async def qa(req: Request):
    body = await req.json()
    question = body.get('question')
    top_k = int(body.get('top_k', 3))
    if not question:
        return {'error': 'missing question'}

    t0 = time.perf_counter()
    sources = retriever.retrieve(question, k=top_k)
    t_retrieval = (time.perf_counter() - t0) * 1000.0

    t1 = time.perf_counter()
    rag_answer = model.answer(question, sources)
    t_llm_rag = (time.perf_counter() - t1) * 1000.0

    t2 = time.perf_counter()
    baseline_answer = model.answer(question, [])
    t_llm_baseline = (time.perf_counter() - t2) * 1000.0

    return {
        'question': question,
        'rag_answer': rag_answer,
        'baseline_answer': baseline_answer,
        'sources': sources,
        'timings': {
            'retrieval_ms': round(t_retrieval, 2),
            'llm_rag_ms': round(t_llm_rag, 2),
            'llm_baseline_ms': round(t_llm_baseline, 2),
        },
    }
