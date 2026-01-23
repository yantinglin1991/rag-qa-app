import os
import json
import time
from pathlib import Path

def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into overlapping chunks for embedding
    
    Args:
        text: Input text to chunk
        chunk_size: Number of characters per chunk
        overlap: Number of overlapping characters between chunks
    
    Returns:
        List of text chunks
    """
    chunks = []
    if not text or len(text) == 0:
        return chunks
    
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end - overlap
        if start >= len(text) - overlap:
            break
    
    return chunks


def process_document(filename, content):
    """
    Process a single document:
    1. Save to data/docs/
    2. Chunk the text
    3. Generate embeddings
    4. Update embeddings.json and index.json
    
    Args:
        filename: Name of the document
        content: Text content of the document
    
    Returns:
        {success, message, chunks_count, embeddings_count}
    """
    try:
        from .retriever import get_embed_model
        
        # Ensure data directories exist
        data_dir = Path(__file__).parent.parent / "data"
        docs_dir = data_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        embeddings_path = data_dir / "embeddings.json"
        index_path = data_dir / "index.json"
        
        # Save document to file
        doc_path = docs_dir / filename
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Chunk the document
        chunks = chunk_text(content)
        if not chunks:
            return {
                "success": False,
                "message": "Document is empty after processing"
            }
        
        # Generate embeddings
        embed_model = get_embed_model()
        if not embed_model:
            return {
                "success": False,
                "message": "Embedding model not available. Install sentence-transformers."
            }
        
        # Load existing embeddings
        embeddings_data = {}
        if embeddings_path.exists():
            try:
                with open(embeddings_path, 'r', encoding='utf-8') as f:
                    embeddings_data = json.load(f)
            except Exception:
                embeddings_data = {}
        
        # Load existing index
        index_data = {}
        if index_path.exists():
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
            except Exception:
                index_data = {}
        
        # Process chunks and generate embeddings
        chunk_embeddings = []
        for i, chunk in enumerate(chunks):
            try:
                embedding = embed_model.encode(chunk).tolist()
                chunk_embeddings.append(embedding)
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Failed to embed chunk {i}: {str(e)}"
                }
        
        # Store embeddings with chunk identifiers
        for i, embedding in enumerate(chunk_embeddings):
            chunk_id = f"{filename}_chunk_{i}"
            embeddings_data[chunk_id] = embedding
        
        # Update index
        index_data[filename] = {
            "path": str(doc_path),
            "chunks": len(chunks),
            "timestamp": time.time(),
            "content_length": len(content)
        }
        
        # Save updated embeddings and index
        with open(embeddings_path, 'w', encoding='utf-8') as f:
            json.dump(embeddings_data, f, ensure_ascii=False, indent=2)
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": f"Document processed successfully",
            "filename": filename,
            "chunks_count": len(chunks),
            "embeddings_count": len(chunk_embeddings)
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing document: {str(e)}"
        }


def get_documents_list():
    """
    Get list of uploaded documents
    
    Returns:
        List of documents with metadata
    """
    try:
        data_dir = Path(__file__).parent.parent / "data"
        index_path = data_dir / "index.json"
        
        if not index_path.exists():
            return []
        
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        documents = []
        for filename, metadata in index_data.items():
            documents.append({
                "filename": filename,
                "chunks": metadata.get("chunks", 0),
                "content_length": metadata.get("content_length", 0),
                "timestamp": metadata.get("timestamp", 0)
            })
        
        return documents
    
    except Exception as e:
        return []


def delete_document(filename):
    """
    Delete a document and its embeddings
    
    Args:
        filename: Name of document to delete
    
    Returns:
        {success, message}
    """
    try:
        data_dir = Path(__file__).parent.parent / "data"
        docs_dir = data_dir / "docs"
        embeddings_path = data_dir / "embeddings.json"
        index_path = data_dir / "index.json"
        
        # Remove document file
        doc_path = docs_dir / filename
        if doc_path.exists():
            doc_path.unlink()
        
        # Remove embeddings for this document
        if embeddings_path.exists():
            with open(embeddings_path, 'r', encoding='utf-8') as f:
                embeddings_data = json.load(f)
            
            # Remove all chunks of this document
            to_remove = [k for k in embeddings_data.keys() if k.startswith(f"{filename}_chunk_")]
            for k in to_remove:
                del embeddings_data[k]
            
            with open(embeddings_path, 'w', encoding='utf-8') as f:
                json.dump(embeddings_data, f, ensure_ascii=False, indent=2)
        
        # Remove from index
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            if filename in index_data:
                del index_data[filename]
            
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": f"Document '{filename}' deleted successfully"
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error deleting document: {str(e)}"
        }
