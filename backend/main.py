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


# ===========================================
# File Upload Endpoints
# ===========================================
from fastapi import File, UploadFile
from services.file_handler import file_handler

@app.post("/api/knowledge-base/upload")
async def upload_file(file: UploadFile = File(...), category: str = "general"):
    """
    העלאת קובץ למאגר הידע
    """
    try:
        result = await file_handler.process_file(file, category)
        
        if result['success']:
            # Add to knowledge base
            await kb_service.add_item(
                title=result['filename'],
                content=result['extracted_text'][:10000],  # Limit content size
                category=category,
                tags=['uploaded', result['metadata']['extension']]
            )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-base/files")
async def list_files(category: str = None):
    """
    קבלת רשימת קבצים שהועלו
    """
    return {"files": file_handler.list_files(category)}


@app.delete("/api/knowledge-base/files/{file_id}")
async def delete_file(file_id: str):
    """
    מחיקת קובץ
    """
    if file_handler.delete_file(file_id):
        return {"success": True, "message": "File deleted"}
    raise HTTPException(status_code=404, detail="File not found")


# ===========================================
# Analytics Endpoints
# ===========================================
from services.analytics import analytics_service

@app.get("/api/admin/analytics")
async def get_analytics(period: str = "7d"):
    """
    קבלת דוח אנליטיקה מלא
    """
    return analytics_service.get_full_report(period)


@app.get("/api/admin/analytics/overview")
async def get_analytics_overview(period: str = "7d"):
    """
    קבלת סקירה כללית
    """
    return analytics_service.get_overview(period)


@app.get("/api/admin/analytics/performance")
async def get_performance_metrics():
    """
    קבלת מדדי ביצועים
    """
    return analytics_service.get_performance_metrics()


@app.post("/api/feedback")
async def submit_feedback(session_id: str, rating: int, feedback: str = None):
    """
    שליחת משוב מהמשתמש
    """
    analytics_service.track_feedback(session_id, rating, feedback)
    return {"success": True, "message": "תודה על המשוב!"}


# ===========================================
# WebSocket Endpoints
# ===========================================
from fastapi import WebSocket, WebSocketDisconnect
from services.websocket_manager import connection_manager, notification_service

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str = None):
    """
    WebSocket endpoint for real-time updates
    """
    await connection_manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get('type') == 'ping':
                await websocket.send_json({'type': 'pong', 'timestamp': data.get('timestamp')})
            elif data.get('type') == 'typing':
                if session_id:
                    await connection_manager.notify_typing(session_id, data.get('is_typing', False))
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        connection_manager.disconnect(websocket, session_id)


@app.websocket("/ws/admin")
async def admin_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for admin notifications
    """
    await connection_manager.connect_admin(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)


@app.get("/api/ws/stats")
async def get_websocket_stats():
    """
    קבלת סטטיסטיקות WebSocket
    """
    return connection_manager.get_connection_stats()


# ===========================================
# Rate Limiting Middleware
# ===========================================
from fastapi import Request
from services.security import rate_limiter, security_service

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware
    """
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit (skip for static files and health checks)
    if not request.url.path.startswith("/static") and request.url.path != "/health":
        result = rate_limiter.is_allowed(client_ip)
        
        if not result['allowed']:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests",
                    "message": "יותר מדי בקשות. נסה שוב מאוחר יותר.",
                    "retry_after": result.get('retry_after', 60)
                },
                headers={"Retry-After": str(result.get('retry_after', 60))}
            )
    
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
