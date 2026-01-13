from typing import Dict, List, Optional
import uuid
from datetime import datetime
from services.llm_service import LLMService
from services.knowledge_base import KnowledgeBaseService
from services.skills_system import SkillsManager
from services.agent_memory import MemoryManager


class ChatManager:
    """
    מנהל השיחות - מתאם בין שירות המודל, מאגר הידע, Skills וMemory
    """
    
    def __init__(self, llm_service: LLMService, kb_service: KnowledgeBaseService):
        self.llm_service = llm_service
        self.kb_service = kb_service
        self.sessions: Dict[str, List[Dict]] = {}
        
        # Initialize Skills System
        self.skills_manager = SkillsManager(kb_service)
        
        # Initialize Memory Manager
        self.memory_manager = MemoryManager()
    
    def _create_session_id(self) -> str:
        """יצירת מזהה ייחודי לסשן"""
        return str(uuid.uuid4())
    
    def _get_or_create_session(self, session_id: Optional[str] = None) -> str:
        """קבלת או יצירת סשן חדש"""
        if session_id and session_id in self.sessions:
            return session_id
        
        new_session_id = self._create_session_id()
        self.sessions[new_session_id] = []
        return new_session_id
    
    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        עיבוד הודעה מהמשתמש עם Skills וMemory
        
        Args:
            message: ההודעה מהמשתמש
            session_id: מזהה הסשן (יווצר אם לא קיים)
            user_id: מזהה המשתמש (אופציונלי)
        
        Returns:
            תשובה עם המידע הרלוונטי
        """
        # קבלת או יצירת סשן
        session_id = self._get_or_create_session(session_id)
        
        # קבלת Memory לסשן
        memory = self.memory_manager.get_or_create_memory(session_id)
        
        # הוספת ההודעה להיסטוריה
        self.sessions[session_id].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Process with Skills System
        skills_results = await self.skills_manager.process_query(message)
        
        # Get relevant memories
        relevant_memories = memory.get_relevant_memories(message, limit=3)
        
        # חיפוש קונטקסט רלוונטי במאגר הידע
        context = await self.kb_service.get_context_for_query(message)
        
        # Build enhanced context with memories and skills
        enhanced_context = context
        if relevant_memories:
            enhanced_context += "\n\nמידע רלוונטי מהיסטוריה:\n" + "\n".join(relevant_memories)
        
        if skills_results['skills_triggered']:
            enhanced_context += f"\n\nSkills שהופעלו: {', '.join(skills_results['skills_triggered'])}"
        
        # קבלת ההיסטוריה (10 הודעות אחרונות)
        recent_messages = self.sessions[session_id][-10:]
        messages_for_llm = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in recent_messages
        ]
        
        # יצירת תשובה מהמודל עם קונטקסט משודרג
        response_content = await self.llm_service.generate_response(
            messages=messages_for_llm,
            context=enhanced_context
        )
        
        # הוספת התשובה להיסטוריה
        self.sessions[session_id].append({
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Store interaction in memory
        memory.add_interaction(
            user_message=message,
            assistant_response=response_content,
            metadata={
                'skills_used': skills_results['skills_triggered'],
                'timestamp': datetime.now().isoformat()
            }
        )
        
        # חיפוש מקורות
        sources = await self.kb_service.search(message, limit=3)
        
        return {
            "response": response_content,
            "session_id": session_id,
            "sources": [
                {
                    "title": s['metadata'].get('title', ''),
                    "category": s['metadata'].get('category', ''),
                    "relevance": 1 - s.get('distance', 1)
                }
                for s in sources
            ],
            "skills_used": skills_results['skills_triggered'],
            "memory_stats": memory.get_statistics()
        }
    
    async def get_history(self, session_id: str) -> List[Dict]:
        """
        קבלת היסטוריית שיחה
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        return self.sessions[session_id]
    
    async def delete_session(self, session_id: str):
        """
        מחיקת סשן וזיכרון
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        # Delete memory as well
        self.memory_manager.delete_session_memory(session_id)
    
    def get_active_sessions(self) -> List[str]:
        """
        קבלת רשימת סשנים פעילים
        """
        return list(self.sessions.keys())
    
    async def get_session_memory(self, session_id: str) -> Dict:
        """
        קבלת זיכרון של סשן
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        memory = self.memory_manager.get_or_create_memory(session_id)
        return memory.export_memory()
    
    def get_available_skills(self) -> List[Dict]:
        """
        קבלת רשימת Skills זמינים
        """
        return self.skills_manager.get_available_skills()
