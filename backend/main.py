from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime

from services.llm_service import LLMService
from services.knowledge_base import KnowledgeBaseService
from services.chat_manager import ChatManager
from routes import admin

app = FastAPI(title="Hotel Management AI Support System")

# הגדרת CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # בפרודקשן יש להגדיר את הדומיינים הספציפיים
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# אתחול שירותים
llm_service = LLMService()
kb_service = KnowledgeBaseService()
chat_manager = ChatManager(llm_service, kb_service)

# Include admin routes
app.include_router(admin.router)


# מודלים
class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: Optional[List[dict]] = None


class KnowledgeBaseItem(BaseModel):
    title: str
    content: str
    category: str
    tags: Optional[List[str]] = []


@app.get("/")
async def root():
    return {
        "message": "Hotel Management AI Support System",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "llm_service": llm_service.is_available(),
        "knowledge_base": kb_service.is_available()
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    נקודת קצה לשיחה עם הבוט
    """
    try:
        response = await chat_manager.process_message(
            message=request.message,
            session_id=request.session_id,
            user_id=request.user_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    קבלת היסטוריית שיחה
    """
    try:
        history = await chat_manager.get_history(session_id)
        return {"session_id": session_id, "messages": history}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/knowledge-base/add")
async def add_knowledge(item: KnowledgeBaseItem):
    """
    הוספת מידע ל-Knowledge Base
    """
    try:
        result = await kb_service.add_item(
            title=item.title,
            content=item.content,
            category=item.category,
            tags=item.tags
        )
        return {"success": True, "id": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-base/search")
async def search_knowledge(query: str, limit: int = 5):
    """
    חיפוש במאגר הידע
    """
    try:
        results = await kb_service.search(query, limit=limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/chat/session/{session_id}")
async def delete_session(session_id: str):
    """
    מחיקת session
    """
    try:
        await chat_manager.delete_session(session_id)
        return {"success": True, "message": "Session deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skills")
async def get_skills():
    """
    קבלת רשימת Skills זמינים
    """
    try:
        skills = chat_manager.get_available_skills()
        return {"skills": skills}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}/memory")
async def get_session_memory(session_id: str):
    """
    קבלת זיכרון של סשן
    """
    try:
        memory = await chat_manager.get_session_memory(session_id)
        return memory
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
