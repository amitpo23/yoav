"""
Advanced Memory Service - Long-term and Short-term Memory Management
מערכת זיכרון מתקדמת עם יכולות למידה
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class Memory:
    """יחידת זיכרון בודדת"""
    id: str
    content: str
    memory_type: str  # 'fact', 'preference', 'interaction', 'learning'
    source: str  # 'user', 'system', 'scraped'
    importance: float  # 0.0 - 1.0
    created_at: str
    last_accessed: str
    access_count: int
    context: Dict[str, Any]
    embedding_key: Optional[str] = None
    expires_at: Optional[str] = None


@dataclass 
class ConversationContext:
    """הקשר שיחה נוכחי"""
    session_id: str
    user_name: Optional[str]
    user_role: Optional[str]
    current_topic: str
    previous_topics: List[str]
    entities_mentioned: Dict[str, List[str]]
    sentiment: str
    urgency: str
    language: str


class AdvancedMemoryService:
    """
    שירות זיכרון מתקדם עם:
    - זיכרון לטווח קצר (שיחה נוכחית)
    - זיכרון לטווח ארוך (עובדות, העדפות, למידה)
    - זיהוי דפוסים
    - למידה מהתנהגות משתמש
    """
    
    def __init__(self, storage_path: str = "./data/memory"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Short-term memory (per session)
        self.short_term: Dict[str, List[Dict]] = defaultdict(list)
        
        # Long-term memory (persistent)
        self.long_term: Dict[str, Memory] = {}
        
        # User profiles
        self.user_profiles: Dict[str, Dict] = {}
        
        # Learned patterns
        self.patterns: Dict[str, Dict] = {}
        
        # Conversation contexts
        self.contexts: Dict[str, ConversationContext] = {}
        
        # Load existing memories
        self._load_memories()
    
    def _load_memories(self):
        """טעינת זיכרונות מהקבצים"""
        try:
            # Load long-term memories
            lt_path = os.path.join(self.storage_path, "long_term.json")
            if os.path.exists(lt_path):
                with open(lt_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for mem_id, mem_data in data.items():
                        self.long_term[mem_id] = Memory(**mem_data)
            
            # Load user profiles
            profiles_path = os.path.join(self.storage_path, "user_profiles.json")
            if os.path.exists(profiles_path):
                with open(profiles_path, 'r', encoding='utf-8') as f:
                    self.user_profiles = json.load(f)
            
            # Load patterns
            patterns_path = os.path.join(self.storage_path, "patterns.json")
            if os.path.exists(patterns_path):
                with open(patterns_path, 'r', encoding='utf-8') as f:
                    self.patterns = json.load(f)
                    
        except Exception as e:
            print(f"Error loading memories: {e}")
    
    def _save_memories(self):
        """שמירת זיכרונות לקבצים"""
        try:
            # Save long-term memories
            lt_path = os.path.join(self.storage_path, "long_term.json")
            with open(lt_path, 'w', encoding='utf-8') as f:
                data = {k: asdict(v) for k, v in self.long_term.items()}
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Save user profiles
            profiles_path = os.path.join(self.storage_path, "user_profiles.json")
            with open(profiles_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_profiles, f, ensure_ascii=False, indent=2)
            
            # Save patterns
            patterns_path = os.path.join(self.storage_path, "patterns.json")
            with open(patterns_path, 'w', encoding='utf-8') as f:
                json.dump(self.patterns, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error saving memories: {e}")
    
    def _generate_id(self, content: str) -> str:
        """יצירת ID ייחודי לזיכרון"""
        return hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
    
    # ==================== Short-Term Memory ====================
    
    async def add_to_short_term(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """הוספת הודעה לזיכרון קצר טווח"""
        memory_item = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.short_term[session_id].append(memory_item)
        
        # Limit short-term memory size
        if len(self.short_term[session_id]) > 50:
            self.short_term[session_id] = self.short_term[session_id][-50:]
    
    async def get_short_term(self, session_id: str, limit: int = 20) -> List[Dict]:
        """קבלת זיכרון קצר טווח"""
        return self.short_term[session_id][-limit:]
    
    async def get_conversation_summary(self, session_id: str) -> str:
        """יצירת סיכום שיחה"""
        messages = self.short_term.get(session_id, [])
        if not messages:
            return "אין היסטוריית שיחה"
        
        topics = set()
        for msg in messages:
            content = msg.get("content", "").lower()
            # Extract key topics
            if "הזמנ" in content:
                topics.add("הזמנות")
            if "חדר" in content:
                topics.add("חדרים")
            if "תשלום" in content or "חשבון" in content:
                topics.add("תשלומים")
            if "בעי" in content or "שגיא" in content:
                topics.add("תקלות")
        
        return f"נושאים שנדונו: {', '.join(topics) if topics else 'כללי'}"
    
    # ==================== Long-Term Memory ====================
    
    async def remember(
        self,
        content: str,
        memory_type: str = "fact",
        source: str = "system",
        importance: float = 0.5,
        context: Optional[Dict] = None,
        expires_in_days: Optional[int] = None
    ) -> str:
        """שמירת מידע בזיכרון ארוך טווח"""
        memory_id = self._generate_id(content)
        now = datetime.now().isoformat()
        
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        memory = Memory(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            source=source,
            importance=importance,
            created_at=now,
            last_accessed=now,
            access_count=0,
            context=context or {},
            expires_at=expires_at
        )
        
        self.long_term[memory_id] = memory
        self._save_memories()
        
        return memory_id
    
    async def recall(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Memory]:
        """חיפוש בזיכרון ארוך טווח"""
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for memory in self.long_term.values():
            # Check expiration
            if memory.expires_at:
                if datetime.fromisoformat(memory.expires_at) < datetime.now():
                    continue
            
            # Filter by type
            if memory_types and memory.memory_type not in memory_types:
                continue
            
            # Calculate relevance
            content_lower = memory.content.lower()
            content_words = set(content_lower.split())
            
            # Word overlap score
            overlap = len(query_words & content_words)
            if overlap == 0:
                continue
            
            relevance = (overlap / len(query_words)) * memory.importance
            
            # Boost by access count (popularity)
            relevance *= (1 + memory.access_count * 0.1)
            
            results.append((relevance, memory))
        
        # Sort by relevance
        results.sort(key=lambda x: x[0], reverse=True)
        
        # Update access counts
        for _, memory in results[:limit]:
            memory.last_accessed = datetime.now().isoformat()
            memory.access_count += 1
        
        self._save_memories()
        
        return [mem for _, mem in results[:limit]]
    
    async def forget(self, memory_id: str) -> bool:
        """מחיקת זיכרון"""
        if memory_id in self.long_term:
            del self.long_term[memory_id]
            self._save_memories()
            return True
        return False
    
    # ==================== User Profiles ====================
    
    async def update_user_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ):
        """עדכון פרופיל משתמש"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "created_at": datetime.now().isoformat(),
                "preferences": {},
                "history": [],
                "expertise_level": "beginner",
                "common_issues": [],
                "satisfaction_score": 0.0
            }
        
        profile = self.user_profiles[user_id]
        profile.update(updates)
        profile["last_updated"] = datetime.now().isoformat()
        
        self._save_memories()
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """קבלת פרופיל משתמש"""
        return self.user_profiles.get(user_id)
    
    # ==================== Pattern Learning ====================
    
    async def learn_pattern(
        self,
        pattern_name: str,
        pattern_data: Dict[str, Any]
    ):
        """למידת דפוס חדש"""
        if pattern_name not in self.patterns:
            self.patterns[pattern_name] = {
                "occurrences": 0,
                "first_seen": datetime.now().isoformat(),
                "data": pattern_data
            }
        
        self.patterns[pattern_name]["occurrences"] += 1
        self.patterns[pattern_name]["last_seen"] = datetime.now().isoformat()
        self.patterns[pattern_name]["data"].update(pattern_data)
        
        self._save_memories()
    
    async def get_relevant_patterns(self, context: str) -> List[Dict]:
        """קבלת דפוסים רלוונטיים"""
        relevant = []
        context_lower = context.lower()
        
        for name, pattern in self.patterns.items():
            if name.lower() in context_lower or \
               any(str(v).lower() in context_lower for v in pattern.get("data", {}).values()):
                relevant.append({"name": name, **pattern})
        
        return sorted(relevant, key=lambda x: x["occurrences"], reverse=True)
    
    # ==================== Context Management ====================
    
    async def update_context(
        self,
        session_id: str,
        topic: Optional[str] = None,
        entities: Optional[Dict[str, List[str]]] = None,
        sentiment: Optional[str] = None,
        urgency: Optional[str] = None
    ) -> ConversationContext:
        """עדכון הקשר שיחה"""
        if session_id not in self.contexts:
            self.contexts[session_id] = ConversationContext(
                session_id=session_id,
                user_name=None,
                user_role=None,
                current_topic="general",
                previous_topics=[],
                entities_mentioned={},
                sentiment="neutral",
                urgency="normal",
                language="he"
            )
        
        ctx = self.contexts[session_id]
        
        if topic and topic != ctx.current_topic:
            ctx.previous_topics.append(ctx.current_topic)
            ctx.current_topic = topic
        
        if entities:
            for key, values in entities.items():
                if key not in ctx.entities_mentioned:
                    ctx.entities_mentioned[key] = []
                ctx.entities_mentioned[key].extend(values)
        
        if sentiment:
            ctx.sentiment = sentiment
        
        if urgency:
            ctx.urgency = urgency
        
        return ctx
    
    async def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """קבלת הקשר שיחה"""
        return self.contexts.get(session_id)
    
    # ==================== Memory Stats ====================
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """קבלת סטטיסטיקות זיכרון"""
        return {
            "short_term_sessions": len(self.short_term),
            "long_term_memories": len(self.long_term),
            "user_profiles": len(self.user_profiles),
            "learned_patterns": len(self.patterns),
            "active_contexts": len(self.contexts),
            "memory_by_type": self._count_by_type(),
            "memory_by_source": self._count_by_source(),
            "total_access_count": sum(m.access_count for m in self.long_term.values())
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """ספירת זיכרונות לפי סוג"""
        counts = defaultdict(int)
        for memory in self.long_term.values():
            counts[memory.memory_type] += 1
        return dict(counts)
    
    def _count_by_source(self) -> Dict[str, int]:
        """ספירת זיכרונות לפי מקור"""
        counts = defaultdict(int)
        for memory in self.long_term.values():
            counts[memory.source] += 1
        return dict(counts)
    
    # ==================== Cleanup ====================
    
    async def cleanup_expired(self) -> int:
        """ניקוי זיכרונות שפג תוקפם"""
        now = datetime.now()
        expired_ids = []
        
        for mem_id, memory in self.long_term.items():
            if memory.expires_at:
                if datetime.fromisoformat(memory.expires_at) < now:
                    expired_ids.append(mem_id)
        
        for mem_id in expired_ids:
            del self.long_term[mem_id]
        
        if expired_ids:
            self._save_memories()
        
        return len(expired_ids)


# Singleton instance
memory_service = AdvancedMemoryService()
