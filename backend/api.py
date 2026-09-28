import os
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Import our existing logic
from rag.pipeline import run_interview_prep, force_reindex
from client.orchestrator import process_user_request
from client.extractor import extract_and_save

app = FastAPI(title="Smart Job Assistant API")

# Allow Next.js frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

class RAGRequest(BaseModel):
    prompt: str

@app.post("/api/rag")
async def rag_endpoint(request: RAGRequest):
    try:
        result = run_interview_prep(request.prompt)
        return {"result": result}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reindex")
async def reindex_endpoint():
    """Force re-index the RAG knowledge base after updating data files."""
    try:
        result = force_reindex()
        return {"status": "success", "message": result}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orchestrator")
async def orchestrator_endpoint(request: ChatRequest):
    try:
        # process_user_request is async
        result = await process_user_request(request.prompt)
        return {"result": result}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/extract")
async def extract_endpoint(text: Optional[str] = Form(None), file: Optional[UploadFile] = File(None)):
    try:
        if file:
            # Save uploaded file to a temporary file
            suffix = os.path.splitext(file.filename)[1] if file.filename else ""
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            result = await extract_and_save(tmp_path)
            os.remove(tmp_path)
            return {"result": result}
        elif text:
            result = await extract_and_save(text)
            return {"result": result}
        else:
            raise HTTPException(status_code=400, detail="Must provide either text or a file")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
