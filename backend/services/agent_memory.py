from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json


class MemoryEntry:
    """Single memory entry"""
    
    def __init__(self, content: str, category: str, importance: float = 0.5):
        self.content = content
        self.category = category
        self.importance = importance
        self.timestamp = datetime.now()
        self.access_count = 0
        self.last_accessed = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'content': self.content,
            'category': self.category,
            'importance': self.importance,
            'timestamp': self.timestamp.isoformat(),
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat()
        }
    
    def access(self):
        """Record memory access"""
        self.access_count += 1
        self.last_accessed = datetime.now()


class AgentMemory:
    """
    Memory system for the AI agent
    Stores conversation context, user preferences, and learned information
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.short_term_memory: List[MemoryEntry] = []  # Recent interactions
        self.long_term_memory: List[MemoryEntry] = []   # Important information
        self.user_profile: Dict[str, Any] = {}           # User preferences and info
        self.conversation_summary: str = ""
        self.topics_discussed: List[str] = []
        self.created_at = datetime.now()
    
    def add_interaction(self, user_message: str, assistant_response: str, metadata: Optional[Dict] = None):
        """Add an interaction to short-term memory"""
        interaction = {
            'user': user_message,
            'assistant': assistant_response,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        
        entry = MemoryEntry(
            content=json.dumps(interaction),
            category='interaction',
            importance=0.5
        )
        
        self.short_term_memory.append(entry)
        
        # Extract topics
        self._extract_topics(user_message)
        
        # Move important memories to long-term if needed
        if len(self.short_term_memory) > 20:
            self._consolidate_memory()
    
    def add_fact(self, fact: str, category: str = 'general', importance: float = 0.7):
        """Add a fact to long-term memory"""
        entry = MemoryEntry(
            content=fact,
            category=category,
            importance=importance
        )
        self.long_term_memory.append(entry)
    
    def update_user_profile(self, key: str, value: Any):
        """Update user profile information"""
        self.user_profile[key] = value
        
        # Store in long-term memory
        self.add_fact(
            f"User preference: {key} = {value}",
            category='user_profile',
            importance=0.8
        )
    
    def get_context(self, n_recent: int = 5) -> str:
        """Get recent conversation context"""
        recent = self.short_term_memory[-n_recent:] if len(self.short_term_memory) >= n_recent else self.short_term_memory
        
        context_parts = []
        for entry in recent:
            entry.access()
            try:
                interaction = json.loads(entry.content)
                context_parts.append(f"משתמש: {interaction['user']}")
                context_parts.append(f"עוזר: {interaction['assistant']}")
            except:
                context_parts.append(entry.content)
        
        return "\n".join(context_parts)
    
    def get_relevant_memories(self, query: str, limit: int = 3) -> List[str]:
        """Get relevant memories based on query"""
        relevant = []
        
        # Simple keyword matching (can be improved with embeddings)
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        all_memories = self.short_term_memory + self.long_term_memory
        
        # Score memories by relevance
        scored_memories = []
        for memory in all_memories:
            memory_lower = memory.content.lower()
            memory_words = set(memory_lower.split())
            
            # Calculate overlap
            overlap = len(query_words & memory_words)
            score = overlap * memory.importance
            
            if score > 0:
                scored_memories.append((score, memory))
        
        # Sort by score and get top results
        scored_memories.sort(reverse=True, key=lambda x: x[0])
        
        for score, memory in scored_memories[:limit]:
            memory.access()
            relevant.append(memory.content)
        
        return relevant
    
    def summarize_conversation(self) -> str:
        """Generate a summary of the conversation"""
        if not self.short_term_memory:
            return "לא היו שיחות בסשן זה"
        
        topics = ", ".join(self.topics_discussed[-5:]) if self.topics_discussed else "כללי"
        interactions_count = len(self.short_term_memory)
        
        summary = f"סשן זה כלל {interactions_count} אינטראקציות. "
        summary += f"נושאים עיקריים: {topics}. "
        
        if self.user_profile:
            summary += f"פרופיל משתמש: {len(self.user_profile)} העדפות נשמרו."
        
        self.conversation_summary = summary
        return summary
    
    def _extract_topics(self, message: str):
        """Extract topics from message"""
        topic_keywords = {
            'הזמנות': ['הזמנה', 'book', 'reservation'],
            'דוחות': ['דוח', 'report', 'סטטיסטיקה'],
            'חדרים': ['חדר', 'room'],
            'תשלומים': ['תשלום', 'payment', 'כסף'],
            'תמיכה טכנית': ['בעיה', 'שגיאה', 'תקלה'],
            'התחברות': ['התחבר', 'login', 'סיסמה']
        }
        
        message_lower = message.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                if topic not in self.topics_discussed:
                    self.topics_discussed.append(topic)
    
    def _consolidate_memory(self):
        """Move important short-term memories to long-term"""
        # Sort by importance and access count
        sorted_memories = sorted(
            self.short_term_memory,
            key=lambda x: (x.importance, x.access_count),
            reverse=True
        )
        
        # Move top 5 to long-term
        for memory in sorted_memories[:5]:
            if memory.importance > 0.6 or memory.access_count > 2:
                self.long_term_memory.append(memory)
        
        # Keep only recent 10 in short-term
        self.short_term_memory = self.short_term_memory[-10:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            'session_id': self.session_id,
            'short_term_count': len(self.short_term_memory),
            'long_term_count': len(self.long_term_memory),
            'topics_discussed': self.topics_discussed,
            'user_profile_entries': len(self.user_profile),
            'conversation_duration': str(datetime.now() - self.created_at),
            'total_interactions': len(self.short_term_memory)
        }
    
    def export_memory(self) -> Dict[str, Any]:
        """Export all memory data"""
        return {
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'short_term_memory': [m.to_dict() for m in self.short_term_memory],
            'long_term_memory': [m.to_dict() for m in self.long_term_memory],
            'user_profile': self.user_profile,
            'topics_discussed': self.topics_discussed,
            'conversation_summary': self.conversation_summary
        }


class MemoryManager:
    """
    Manages memory for multiple sessions
    """
    
    def __init__(self):
        self.sessions: Dict[str, AgentMemory] = {}
    
    def get_or_create_memory(self, session_id: str) -> AgentMemory:
        """Get existing memory or create new one"""
        if session_id not in self.sessions:
            self.sessions[session_id] = AgentMemory(session_id)
        return self.sessions[session_id]
    
    def delete_session_memory(self, session_id: str):
        """Delete memory for a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_all_sessions(self) -> List[str]:
        """Get all active session IDs"""
        return list(self.sessions.keys())
    
    def cleanup_old_sessions(self, hours: int = 24):
        """Clean up sessions older than specified hours"""
        now = datetime.now()
        to_delete = []
        
        for session_id, memory in self.sessions.items():
            age = now - memory.created_at
            if age > timedelta(hours=hours):
                to_delete.append(session_id)
        
        for session_id in to_delete:
            del self.sessions[session_id]
        
        return len(to_delete)
