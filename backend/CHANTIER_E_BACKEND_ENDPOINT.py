// Backend Enhancement: Return Parcours URL + Case Hash
// File: backend/app/routes/chat.py (or FastAPI endpoint handler)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib
import json

router = APIRouter(prefix="/api/v1", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class ChatResponse(BaseModel):
    answer: str  # RAG response (Q2 + Q3 text)
    case_id: str  # UC ID from Excel
    case_hash: str  # URL-safe hash
    parcours_url: str  # Link to parcours page
    matching_score: float
    source_metadata: dict = {}

def generate_case_hash(case_id: str, salt: str) -> str:
    """Generate URL-safe hash from case ID + salt (deterministic)"""
    data = f"{case_id}|{salt}".encode('utf-8')
    hash_obj = hashlib.sha256(data).digest()
    # Convert to URL-safe string (base62 or custom)
    hash_hex = hash_obj.hex()[:16]  # Use first 16 chars
    return hash_hex

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint that returns:
    1. RAG response (text)
    2. Case hash
    3. Link to parcours page
    """
    try:
        # 1. Query RAG (existing logic)
        rag_result = query_rag_with_metadata(request.message)  # Your existing RAG function
        
        case_id = rag_result.get('case_id', 'unknown')
        case_title = rag_result.get('case_title', '')
        matching_score = rag_result.get('score', 0.0)
        steps_text = rag_result.get('steps', '')  # Q2 + Q3 from Excel
        
        # 2. Generate case hash (deterministic)
        salt = os.getenv('AVOULIA_SALT', 'default-salt')
        case_hash = generate_case_hash(case_id, salt)
        
        # 3. Build parcours URL
        # Dev: http://localhost:5173/action/{case_hash}/
        # Prod: https://avoulia.azurewebsites.net/action/{case_hash}/
        parcours_base_url = os.getenv('PARCOURS_BASE_URL', 'https://localhost:5173')
        parcours_url = f"{parcours_base_url}/action/{case_hash}/"
        
        # 4. Assemble response
        response = ChatResponse(
            answer=steps_text,  # Étapes Q2-Q3 from RAG
            case_id=case_id,
            case_hash=case_hash,
            parcours_url=parcours_url,
            matching_score=matching_score,
            source_metadata={
                'case_title': case_title,
                'intent': rag_result.get('intent', ''),
                'domain': rag_result.get('domain', '')
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Required environment variables:
# AVOULIA_SALT = "prod-salt-value-fixed-forever"  # Never rotate in prod
# PARCOURS_BASE_URL = "https://avoulia.azurewebsites.net" (prod) or "http://localhost:5173" (dev)
