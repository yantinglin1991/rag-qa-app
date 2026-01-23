from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys
from .model_loader import ModelLoader
from .retriever import Retriever
from .document_processor import process_document, get_documents_list, delete_document
import time

app = FastAPI()
model = ModelLoader()
retriever = Retriever()

# Determine base directory for static files
def find_static_dir():
    # List of possible paths to check
    possible_paths = []
    
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller executable
        base = sys._MEIPASS
        possible_paths = [
            os.path.join(base, 'static'),
            os.path.join(base, '..', 'static'),
            os.path.join(os.path.dirname(base), 'static'),
        ]
    else:
        # Running as Python script
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        possible_paths = [os.path.join(base, 'static')]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return possible_paths[0]  # Return first path even if not exists

static_dir = find_static_dir()

# Serve static files
if os.path.exists(static_dir):
    app.mount('/static', StaticFiles(directory=static_dir), name='static')


@app.get('/')
async def root():
    index_file = os.path.join(static_dir, 'index.html')
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {'message': 'index.html not found', 'static_dir': static_dir, 'exists': os.path.exists(static_dir)}


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


@app.post('/upload-doc')
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document for the knowledge base"""
    try:
        content = await file.read()
        text = content.decode('utf-8')
        
        result = process_document(file.filename, text)
        return result
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Upload failed: {str(e)}'
        }


@app.get('/documents')
async def list_documents():
    """Get list of uploaded documents"""
    try:
        docs = get_documents_list()
        return {
            'success': True,
            'documents': docs,
            'count': len(docs)
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to list documents: {str(e)}'
        }


@app.delete('/documents/{filename}')
async def delete_doc(filename: str):
    """Delete a document from the knowledge base"""
    try:
        # Prevent directory traversal attacks
        if '/' in filename or '\\' in filename:
            return {
                'success': False,
                'message': 'Invalid filename'
            }
        
        result = delete_document(filename)
        return result
    except Exception as e:
        return {
            'success': False,
            'message': f'Delete failed: {str(e)}'
        }
