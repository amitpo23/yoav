"""
Conversation Logs & Reports Service
לוגים ודוחות שיחות
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class ConversationLog:
    """לוג שיחה בודדת"""
    session_id: str
    timestamp: str
    role: str  # 'user' or 'assistant'
    message: str
    response_time_ms: Optional[int] = None
    skills_used: Optional[List[str]] = None
    knowledge_sources: Optional[List[str]] = None
    user_satisfaction: Optional[int] = None  # 1-5


@dataclass
class DailyReport:
    """דוח יומי"""
    date: str
    total_conversations: int
    total_messages: int
    unique_users: int
    avg_messages_per_session: float
    avg_response_time_ms: float
    top_topics: List[Dict[str, Any]]
    skills_usage: Dict[str, int]
    satisfaction_avg: float
    peak_hours: List[int]


class ConversationLogsService:
    """
    שירות לניהול לוגים ודוחות שיחות
    """
    
    def __init__(self, storage_path: str = "./data/logs"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        self.logs: List[ConversationLog] = []
        self.daily_stats: Dict[str, Dict] = {}
        
        self._load_logs()
    
    def _load_logs(self):
        """טעינת לוגים מקובץ"""
        try:
            logs_file = os.path.join(self.storage_path, "conversation_logs.json")
            if os.path.exists(logs_file):
                with open(logs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logs = [ConversationLog(**log) for log in data]
            
            stats_file = os.path.join(self.storage_path, "daily_stats.json")
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    self.daily_stats = json.load(f)
        except Exception as e:
            print(f"Error loading logs: {e}")
    
    def _save_logs(self):
        """שמירת לוגים לקובץ"""
        try:
            logs_file = os.path.join(self.storage_path, "conversation_logs.json")
            with open(logs_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(log) for log in self.logs[-10000:]], f, ensure_ascii=False, indent=2)
            
            stats_file = os.path.join(self.storage_path, "daily_stats.json")
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.daily_stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving logs: {e}")
    
    async def log_message(
        self,
        session_id: str,
        role: str,
        message: str,
        response_time_ms: Optional[int] = None,
        skills_used: Optional[List[str]] = None,
        knowledge_sources: Optional[List[str]] = None
    ):
        """הוספת לוג הודעה"""
        log = ConversationLog(
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            role=role,
            message=message[:500],  # Limit message size
            response_time_ms=response_time_ms,
            skills_used=skills_used,
            knowledge_sources=knowledge_sources
        )
        
        self.logs.append(log)
        self._update_daily_stats(log)
        
        # Save every 10 messages
        if len(self.logs) % 10 == 0:
            self._save_logs()
    
    def _update_daily_stats(self, log: ConversationLog):
        """עדכון סטטיסטיקות יומיות"""
        date = log.timestamp[:10]  # YYYY-MM-DD
        hour = int(log.timestamp[11:13])
        
        if date not in self.daily_stats:
            self.daily_stats[date] = {
                "messages": 0,
                "sessions": set(),
                "response_times": [],
                "skills": defaultdict(int),
                "hours": defaultdict(int),
                "topics": defaultdict(int)
            }
        
        stats = self.daily_stats[date]
        stats["messages"] += 1
        
        if isinstance(stats["sessions"], set):
            stats["sessions"].add(log.session_id)
        else:
            stats["sessions"] = set(stats["sessions"])
            stats["sessions"].add(log.session_id)
        
        if log.response_time_ms:
            stats["response_times"].append(log.response_time_ms)
        
        if log.skills_used:
            for skill in log.skills_used:
                stats["skills"][skill] = stats["skills"].get(skill, 0) + 1
        
        stats["hours"][str(hour)] = stats["hours"].get(str(hour), 0) + 1
        
        # Extract topics from message
        topics = self._extract_topics(log.message)
        for topic in topics:
            stats["topics"][topic] = stats["topics"].get(topic, 0) + 1
    
    def _extract_topics(self, message: str) -> List[str]:
        """חילוץ נושאים מהודעה"""
        topics = []
        message_lower = message.lower()
        
        topic_keywords = {
            "הזמנות": ["הזמנ", "booking", "reservation"],
            "חדרים": ["חדר", "room", "חדרים"],
            "תשלומים": ["תשלום", "חשבון", "payment", "invoice"],
            "צ'ק-אין": ["check-in", "צ'ק אין", "כניסה"],
            "צ'ק-אאוט": ["check-out", "צ'ק אאוט", "יציאה"],
            "מחירים": ["מחיר", "price", "rate", "תעריף"],
            "אורחים": ["אורח", "guest", "לקוח"],
            "דוחות": ["דוח", "report", "סטטיסטיק"],
            "הגדרות": ["הגדר", "setting", "config"],
            "תקלות": ["תקלה", "בעי", "error", "שגיא"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in message_lower for kw in keywords):
                topics.append(topic)
        
        return topics if topics else ["כללי"]
    
    async def get_logs(
        self,
        session_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """קבלת לוגים עם פילטרים"""
        filtered_logs = self.logs
        
        if session_id:
            filtered_logs = [l for l in filtered_logs if l.session_id == session_id]
        
        if start_date:
            filtered_logs = [l for l in filtered_logs if l.timestamp >= start_date]
        
        if end_date:
            filtered_logs = [l for l in filtered_logs if l.timestamp <= end_date]
        
        total = len(filtered_logs)
        paginated = filtered_logs[offset:offset + limit]
        
        return {
            "logs": [asdict(log) for log in paginated],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    async def get_session_conversation(self, session_id: str) -> List[Dict]:
        """קבלת שיחה מלאה לפי session_id"""
        session_logs = [l for l in self.logs if l.session_id == session_id]
        session_logs.sort(key=lambda x: x.timestamp)
        return [asdict(log) for log in session_logs]
    
    async def generate_daily_report(self, date: str) -> Optional[DailyReport]:
        """יצירת דוח יומי"""
        if date not in self.daily_stats:
            return None
        
        stats = self.daily_stats[date]
        
        # Convert sets to lists for JSON serialization
        sessions = stats["sessions"] if isinstance(stats["sessions"], set) else set(stats.get("sessions", []))
        
        # Calculate averages
        response_times = stats.get("response_times", [])
        avg_response = sum(response_times) / len(response_times) if response_times else 0
        
        # Top topics
        topics = stats.get("topics", {})
        top_topics = sorted(
            [{"topic": k, "count": v} for k, v in topics.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:10]
        
        # Peak hours
        hours = stats.get("hours", {})
        peak_hours = sorted(
            [(int(h), c) for h, c in hours.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return DailyReport(
            date=date,
            total_conversations=len(sessions),
            total_messages=stats.get("messages", 0),
            unique_users=len(sessions),
            avg_messages_per_session=stats.get("messages", 0) / max(len(sessions), 1),
            avg_response_time_ms=avg_response,
            top_topics=top_topics,
            skills_usage=dict(stats.get("skills", {})),
            satisfaction_avg=0.0,  # TODO: Implement
            peak_hours=[h[0] for h in peak_hours]
        )
    
    async def generate_weekly_report(self) -> Dict[str, Any]:
        """יצירת דוח שבועי"""
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        
        weekly_data = {
            "period": f"{week_ago.strftime('%Y-%m-%d')} - {today.strftime('%Y-%m-%d')}",
            "total_messages": 0,
            "total_sessions": 0,
            "daily_breakdown": [],
            "top_topics": defaultdict(int),
            "skills_usage": defaultdict(int),
            "avg_response_time": 0,
            "response_times": []
        }
        
        for i in range(7):
            date = (week_ago + timedelta(days=i+1)).strftime("%Y-%m-%d")
            if date in self.daily_stats:
                stats = self.daily_stats[date]
                sessions = stats["sessions"] if isinstance(stats["sessions"], set) else set(stats.get("sessions", []))
                
                weekly_data["total_messages"] += stats.get("messages", 0)
                weekly_data["total_sessions"] += len(sessions)
                weekly_data["daily_breakdown"].append({
                    "date": date,
                    "messages": stats.get("messages", 0),
                    "sessions": len(sessions)
                })
                
                for topic, count in stats.get("topics", {}).items():
                    weekly_data["top_topics"][topic] += count
                
                for skill, count in stats.get("skills", {}).items():
                    weekly_data["skills_usage"][skill] += count
                
                weekly_data["response_times"].extend(stats.get("response_times", []))
        
        if weekly_data["response_times"]:
            weekly_data["avg_response_time"] = sum(weekly_data["response_times"]) / len(weekly_data["response_times"])
        
        weekly_data["top_topics"] = sorted(
            [{"topic": k, "count": v} for k, v in weekly_data["top_topics"].items()],
            key=lambda x: x["count"],
            reverse=True
        )[:10]
        
        weekly_data["skills_usage"] = dict(weekly_data["skills_usage"])
        del weekly_data["response_times"]
        
        return weekly_data
    
    async def get_real_time_stats(self) -> Dict[str, Any]:
        """סטטיסטיקות בזמן אמת"""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        hour_ago = (now - timedelta(hours=1)).isoformat()
        
        # Last hour messages
        recent_logs = [l for l in self.logs if l.timestamp >= hour_ago]
        
        # Today stats
        today_stats = self.daily_stats.get(today, {})
        today_sessions = today_stats.get("sessions", set())
        if not isinstance(today_sessions, set):
            today_sessions = set(today_sessions)
        
        return {
            "messages_last_hour": len(recent_logs),
            "active_sessions_today": len(today_sessions),
            "messages_today": today_stats.get("messages", 0),
            "current_hour": now.hour,
            "last_message_time": self.logs[-1].timestamp if self.logs else None
        }
    
    async def export_logs(self, format: str = "json") -> str:
        """ייצוא לוגים"""
        if format == "json":
            return json.dumps([asdict(log) for log in self.logs], ensure_ascii=False, indent=2)
        elif format == "csv":
            lines = ["session_id,timestamp,role,message,response_time_ms"]
            for log in self.logs:
                msg = log.message.replace('"', '""').replace('\n', ' ')
                lines.append(f'"{log.session_id}","{log.timestamp}","{log.role}","{msg}",{log.response_time_ms or ""}')
            return "\n".join(lines)
        return ""


# Singleton instance
logs_service = ConversationLogsService()
