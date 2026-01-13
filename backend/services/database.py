"""
Database Service
Persistent storage for sessions, messages, and data
Using SQLite for simplicity (can be replaced with PostgreSQL)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import sqlite3
import json
import os
from contextlib import contextmanager


class DatabaseService:
    """
    SQLite-based persistent storage service
    """
    
    def __init__(self, db_path: str = "data/hotel_ai.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT DEFAULT '{}'
                )
            ''')
            
            # Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            ''')
            
            # Memory table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT,
                    importance REAL DEFAULT 0.5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            ''')
            
            # Knowledge base items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT,
                    tags TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    embedding_id TEXT
                )
            ''')
            
            # Analytics events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    session_id TEXT,
                    data TEXT DEFAULT '{}',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    message_id INTEGER,
                    rating INTEGER,
                    comment TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_session ON memory(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON analytics_events(event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_activity ON sessions(last_activity)')
    
    # Session methods
    def create_session(self, session_id: str, user_id: str = None, metadata: Dict = None) -> str:
        """Create a new session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (id, user_id, metadata)
                VALUES (?, ?, ?)
            ''', (session_id, user_id, json.dumps(metadata or {})))
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None
    
    def update_session_activity(self, session_id: str):
        """Update session last activity"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE sessions SET last_activity = CURRENT_TIMESTAMP WHERE id = ?
            ''', (session_id,))
    
    def get_active_sessions(self, hours: int = 24) -> List[Dict]:
        """Get sessions active in the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM sessions WHERE last_activity >= ?
            ''', (cutoff,))
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_session(self, session_id: str):
        """Delete a session and its data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
            cursor.execute('DELETE FROM memory WHERE session_id = ?', (session_id,))
            cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    
    def cleanup_old_sessions(self, hours: int = 24) -> int:
        """Delete sessions older than N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get old session IDs
            cursor.execute('SELECT id FROM sessions WHERE last_activity < ?', (cutoff,))
            old_sessions = [row[0] for row in cursor.fetchall()]
            
            if old_sessions:
                placeholders = ','.join('?' * len(old_sessions))
                cursor.execute(f'DELETE FROM messages WHERE session_id IN ({placeholders})', old_sessions)
                cursor.execute(f'DELETE FROM memory WHERE session_id IN ({placeholders})', old_sessions)
                cursor.execute(f'DELETE FROM sessions WHERE id IN ({placeholders})', old_sessions)
            
            return len(old_sessions)
    
    # Message methods
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None) -> int:
        """Add a message to a session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (session_id, role, content, metadata)
                VALUES (?, ?, ?, ?)
            ''', (session_id, role, content, json.dumps(metadata or {})))
            return cursor.lastrowid
    
    def get_messages(self, session_id: str, limit: int = None) -> List[Dict]:
        """Get messages for a session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp'
            if limit:
                query += f' DESC LIMIT {limit}'
            cursor.execute(query, (session_id,))
            messages = [dict(row) for row in cursor.fetchall()]
            if limit:
                messages.reverse()
            return messages
    
    # Memory methods
    def add_memory(self, session_id: str, memory_type: str, content: str, 
                   category: str = None, importance: float = 0.5) -> int:
        """Add a memory entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO memory (session_id, memory_type, content, category, importance)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, memory_type, content, category, importance))
            return cursor.lastrowid
    
    def get_memories(self, session_id: str, memory_type: str = None, limit: int = 10) -> List[Dict]:
        """Get memories for a session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if memory_type:
                cursor.execute('''
                    SELECT * FROM memory WHERE session_id = ? AND memory_type = ?
                    ORDER BY importance DESC, created_at DESC LIMIT ?
                ''', (session_id, memory_type, limit))
            else:
                cursor.execute('''
                    SELECT * FROM memory WHERE session_id = ?
                    ORDER BY importance DESC, created_at DESC LIMIT ?
                ''', (session_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    # Knowledge base methods
    def add_knowledge_item(self, title: str, content: str, category: str = None, 
                          tags: List[str] = None, embedding_id: str = None) -> int:
        """Add a knowledge base item"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO knowledge_items (title, content, category, tags, embedding_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, content, category, json.dumps(tags or []), embedding_id))
            return cursor.lastrowid
    
    def get_knowledge_items(self, category: str = None, limit: int = 100) -> List[Dict]:
        """Get knowledge base items"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute('''
                    SELECT * FROM knowledge_items WHERE category = ?
                    ORDER BY created_at DESC LIMIT ?
                ''', (category, limit))
            else:
                cursor.execute('''
                    SELECT * FROM knowledge_items ORDER BY created_at DESC LIMIT ?
                ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # Analytics methods
    def add_analytics_event(self, event_type: str, session_id: str = None, data: Dict = None):
        """Add an analytics event"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analytics_events (event_type, session_id, data)
                VALUES (?, ?, ?)
            ''', (event_type, session_id, json.dumps(data or {})))
    
    def get_analytics_events(self, event_type: str = None, hours: int = 24) -> List[Dict]:
        """Get analytics events"""
        cutoff = datetime.now() - timedelta(hours=hours)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if event_type:
                cursor.execute('''
                    SELECT * FROM analytics_events 
                    WHERE event_type = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                ''', (event_type, cutoff))
            else:
                cursor.execute('''
                    SELECT * FROM analytics_events WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                ''', (cutoff,))
            return [dict(row) for row in cursor.fetchall()]
    
    # Feedback methods
    def add_feedback(self, session_id: str, rating: int, comment: str = None, message_id: int = None):
        """Add user feedback"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feedback (session_id, message_id, rating, comment)
                VALUES (?, ?, ?, ?)
            ''', (session_id, message_id, rating, comment))
    
    # Statistics
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM sessions')
            total_sessions = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM messages')
            total_messages = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM knowledge_items')
            total_knowledge = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM analytics_events')
            total_events = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(rating) FROM feedback')
            avg_rating = cursor.fetchone()[0] or 0
            
            return {
                'total_sessions': total_sessions,
                'total_messages': total_messages,
                'total_knowledge_items': total_knowledge,
                'total_analytics_events': total_events,
                'average_rating': round(avg_rating, 2)
            }


# Global instance
database_service = DatabaseService()
