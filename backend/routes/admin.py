from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import secrets

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Simple authentication (in production, use proper auth)
ADMIN_TOKENS = set()


def generate_admin_token() -> str:
    """Generate a new admin token"""
    token = secrets.token_urlsafe(32)
    ADMIN_TOKENS.add(token)
    return token


async def verify_admin(authorization: Optional[str] = Header(None)):
    """Verify admin authentication"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization")
    
    token = authorization.replace("Bearer ", "")
    if token not in ADMIN_TOKENS:
        raise HTTPException(status_code=403, detail="Invalid admin token")
    
    return token


# Models
class AdminLogin(BaseModel):
    username: str
    password: str


class AdminStats(BaseModel):
    total_sessions: int
    active_sessions: int
    total_messages: int
    total_knowledge_items: int
    available_skills: int
    uptime: str


class SessionInfo(BaseModel):
    session_id: str
    message_count: int
    created_at: str
    last_activity: str
    topics_discussed: List[str]


class SystemConfig(BaseModel):
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    model: Optional[str] = None
    enable_skills: Optional[bool] = None


# Admin authentication endpoint
@router.post("/login")
async def admin_login(credentials: AdminLogin):
    """
    Login endpoint for admin
    Default: username=admin, password=admin123 (change in production!)
    """
    # Simple authentication (replace with proper auth in production)
    if credentials.username == "admin" and credentials.password == "admin123":
        token = generate_admin_token()
        return {
            "success": True,
            "token": token,
            "message": "התחברת בהצלחה כמנהל"
        }
    
    raise HTTPException(status_code=401, detail="שם משתמש או סיסמה שגויים")


@router.get("/stats", dependencies=[Depends(verify_admin)])
async def get_system_stats():
    """Get system statistics"""
    from main import chat_manager
    
    active_sessions = chat_manager.get_active_sessions()
    total_messages = sum(len(chat_manager.sessions.get(sid, [])) for sid in active_sessions)
    
    # Get knowledge base stats
    kb_count = len(chat_manager.kb_service.items) if chat_manager.kb_service.is_available() else 0
    
    # Get skills count
    skills = chat_manager.get_available_skills()
    
    return AdminStats(
        total_sessions=len(chat_manager.sessions),
        active_sessions=len(active_sessions),
        total_messages=total_messages,
        total_knowledge_items=kb_count,
        available_skills=len(skills),
        uptime="Active"  # Can be calculated from app start time
    )


@router.get("/sessions", dependencies=[Depends(verify_admin)])
async def list_sessions():
    """List all active sessions"""
    from main import chat_manager
    
    sessions_info = []
    for session_id in chat_manager.get_active_sessions():
        try:
            memory = await chat_manager.get_session_memory(session_id)
            stats = memory.get('conversation_summary', '')
            
            sessions_info.append(SessionInfo(
                session_id=session_id,
                message_count=len(chat_manager.sessions.get(session_id, [])),
                created_at=memory.get('created_at', ''),
                last_activity=datetime.now().isoformat(),
                topics_discussed=memory.get('topics_discussed', [])
            ))
        except:
            continue
    
    return {"sessions": sessions_info}


@router.get("/sessions/{session_id}", dependencies=[Depends(verify_admin)])
async def get_session_details(session_id: str):
    """Get detailed information about a session"""
    from main import chat_manager
    
    try:
        history = await chat_manager.get_history(session_id)
        memory = await chat_manager.get_session_memory(session_id)
        
        return {
            "session_id": session_id,
            "history": history,
            "memory": memory
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/sessions/{session_id}", dependencies=[Depends(verify_admin)])
async def delete_session(session_id: str):
    """Delete a session"""
    from main import chat_manager
    
    try:
        await chat_manager.delete_session(session_id)
        return {"success": True, "message": f"Session {session_id} נמחק"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/skills", dependencies=[Depends(verify_admin)])
async def list_skills():
    """List all available skills"""
    from main import chat_manager
    
    skills = chat_manager.get_available_skills()
    return {"skills": skills}


@router.post("/skills/{skill_name}/toggle", dependencies=[Depends(verify_admin)])
async def toggle_skill(skill_name: str, enable: bool):
    """Enable or disable a skill"""
    from main import chat_manager
    
    if enable:
        success = chat_manager.skills_manager.enable_skill(skill_name)
    else:
        success = chat_manager.skills_manager.disable_skill(skill_name)
    
    if success:
        return {"success": True, "message": f"Skill {skill_name} {'הופעל' if enable else 'הושבת'}"}
    
    raise HTTPException(status_code=404, detail="Skill not found")


@router.get("/knowledge-base/stats", dependencies=[Depends(verify_admin)])
async def knowledge_base_stats():
    """Get knowledge base statistics"""
    from main import chat_manager
    
    if not chat_manager.kb_service.is_available():
        return {"error": "Knowledge base not available"}
    
    count = chat_manager.kb_service.collection.count()
    return {
        "total_items": count,
        "collection_name": chat_manager.kb_service.collection.name,
        "status": "active"
    }


@router.post("/knowledge-base/rebuild", dependencies=[Depends(verify_admin)])
async def rebuild_knowledge_base():
    """Rebuild knowledge base with base knowledge"""
    from main import chat_manager
    
    try:
        # Clear existing
        chat_manager.kb_service.collection.delete()
        
        # Re-initialize
        chat_manager.kb_service._initialize_base_knowledge()
        
        return {
            "success": True,
            "message": "מאגר הידע נבנה מחדש",
            "items_count": chat_manager.kb_service.collection.count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/config", dependencies=[Depends(verify_admin)])
async def get_system_config():
    """Get current system configuration"""
    from main import llm_service
    
    return {
        "model": llm_service.model,
        "api_available": llm_service.is_available(),
        "system_prompt_length": len(llm_service.system_prompt)
    }


@router.post("/system/config", dependencies=[Depends(verify_admin)])
async def update_system_config(config: SystemConfig):
    """Update system configuration"""
    from main import llm_service
    
    updated_fields = []
    
    if config.model:
        llm_service.model = config.model
        updated_fields.append("model")
    
    return {
        "success": True,
        "message": "Configuration updated",
        "updated_fields": updated_fields
    }


@router.get("/logs/recent", dependencies=[Depends(verify_admin)])
async def get_recent_logs(limit: int = 50):
    """Get recent system logs (placeholder)"""
    # This would typically read from a log file or logging system
    return {
        "logs": [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "System running normally"
            }
        ]
    }


@router.post("/system/cleanup", dependencies=[Depends(verify_admin)])
async def cleanup_old_sessions(hours: int = 24):
    """Clean up old sessions"""
    from main import chat_manager
    
    deleted = chat_manager.memory_manager.cleanup_old_sessions(hours=hours)
    
    return {
        "success": True,
        "deleted_sessions": deleted,
        "message": f"נוקו {deleted} סשנים ישנים"
    }
