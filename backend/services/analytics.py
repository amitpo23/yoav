"""
Advanced Analytics Service
Provides detailed analytics and insights
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import json


class AnalyticsEvent:
    """Single analytics event"""
    
    def __init__(self, event_type: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'event_type': self.event_type,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }


class AnalyticsService:
    """
    Advanced analytics service for tracking system usage
    """
    
    def __init__(self):
        self.events: List[AnalyticsEvent] = []
        self.session_analytics: Dict[str, Dict] = {}
        self.skill_usage: Dict[str, int] = defaultdict(int)
        self.query_patterns: Dict[str, int] = defaultdict(int)
        self.response_times: List[float] = []
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.user_satisfaction: List[Dict] = []
        self.daily_stats: Dict[str, Dict] = {}
    
    def track_event(self, event_type: str, data: Dict[str, Any]):
        """Track a generic event"""
        event = AnalyticsEvent(event_type, data)
        self.events.append(event)
        
        # Update daily stats
        date_key = datetime.now().strftime('%Y-%m-%d')
        if date_key not in self.daily_stats:
            self.daily_stats[date_key] = {
                'events': 0,
                'messages': 0,
                'sessions': 0,
                'errors': 0
            }
        self.daily_stats[date_key]['events'] += 1
        
        # Keep only last 10000 events
        if len(self.events) > 10000:
            self.events = self.events[-5000:]
    
    def track_message(self, session_id: str, message: str, response: str, 
                      response_time: float, skills_used: List[str] = None):
        """Track a chat message"""
        
        self.track_event('message', {
            'session_id': session_id,
            'message_length': len(message),
            'response_length': len(response),
            'response_time': response_time,
            'skills_used': skills_used or []
        })
        
        # Track response times
        self.response_times.append(response_time)
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-500:]
        
        # Track skill usage
        for skill in (skills_used or []):
            self.skill_usage[skill] += 1
        
        # Track session
        if session_id not in self.session_analytics:
            self.session_analytics[session_id] = {
                'message_count': 0,
                'total_response_time': 0,
                'skills_used': [],
                'started_at': datetime.now().isoformat()
            }
        
        self.session_analytics[session_id]['message_count'] += 1
        self.session_analytics[session_id]['total_response_time'] += response_time
        
        # Update daily stats
        date_key = datetime.now().strftime('%Y-%m-%d')
        if date_key in self.daily_stats:
            self.daily_stats[date_key]['messages'] += 1
    
    def track_session_start(self, session_id: str):
        """Track session start"""
        self.track_event('session_start', {'session_id': session_id})
        
        date_key = datetime.now().strftime('%Y-%m-%d')
        if date_key in self.daily_stats:
            self.daily_stats[date_key]['sessions'] += 1
    
    def track_error(self, error_type: str, error_message: str, session_id: str = None):
        """Track an error"""
        self.track_event('error', {
            'error_type': error_type,
            'error_message': error_message,
            'session_id': session_id
        })
        
        self.error_counts[error_type] += 1
        
        date_key = datetime.now().strftime('%Y-%m-%d')
        if date_key in self.daily_stats:
            self.daily_stats[date_key]['errors'] += 1
    
    def track_feedback(self, session_id: str, rating: int, feedback: str = None):
        """Track user feedback"""
        self.user_satisfaction.append({
            'session_id': session_id,
            'rating': rating,
            'feedback': feedback,
            'timestamp': datetime.now().isoformat()
        })
        
        self.track_event('feedback', {
            'session_id': session_id,
            'rating': rating
        })
    
    def get_overview(self, period: str = '7d') -> Dict:
        """Get analytics overview for a period"""
        
        # Calculate period
        days = int(period.replace('d', '')) if 'd' in period else 7
        start_date = datetime.now() - timedelta(days=days)
        
        # Filter events by period
        period_events = [
            e for e in self.events 
            if e.timestamp >= start_date
        ]
        
        # Calculate metrics
        total_messages = sum(
            1 for e in period_events if e.event_type == 'message'
        )
        
        total_sessions = sum(
            1 for e in period_events if e.event_type == 'session_start'
        )
        
        total_errors = sum(
            1 for e in period_events if e.event_type == 'error'
        )
        
        # Average response time
        period_response_times = [
            e.data.get('response_time', 0) 
            for e in period_events 
            if e.event_type == 'message'
        ]
        avg_response_time = (
            sum(period_response_times) / len(period_response_times)
            if period_response_times else 0
        )
        
        # User satisfaction
        period_feedback = [
            f for f in self.user_satisfaction
            if datetime.fromisoformat(f['timestamp']) >= start_date
        ]
        avg_satisfaction = (
            sum(f['rating'] for f in period_feedback) / len(period_feedback)
            if period_feedback else 0
        )
        
        return {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': datetime.now().isoformat(),
            'total_messages': total_messages,
            'total_sessions': total_sessions,
            'total_errors': total_errors,
            'avg_response_time_ms': round(avg_response_time * 1000, 2),
            'avg_satisfaction': round(avg_satisfaction, 2),
            'error_rate': round(total_errors / max(total_messages, 1) * 100, 2),
            'messages_per_session': round(total_messages / max(total_sessions, 1), 2)
        }
    
    def get_skill_analytics(self) -> Dict:
        """Get skill usage analytics"""
        total_usage = sum(self.skill_usage.values())
        
        skill_data = []
        for skill, count in sorted(self.skill_usage.items(), key=lambda x: -x[1]):
            skill_data.append({
                'skill': skill,
                'count': count,
                'percentage': round(count / max(total_usage, 1) * 100, 2)
            })
        
        return {
            'total_skill_activations': total_usage,
            'skills': skill_data
        }
    
    def get_hourly_distribution(self, days: int = 7) -> Dict:
        """Get hourly message distribution"""
        start_date = datetime.now() - timedelta(days=days)
        
        hourly_counts = defaultdict(int)
        for event in self.events:
            if event.event_type == 'message' and event.timestamp >= start_date:
                hour = event.timestamp.hour
                hourly_counts[hour] += 1
        
        return {
            'distribution': [
                {'hour': h, 'count': hourly_counts.get(h, 0)}
                for h in range(24)
            ]
        }
    
    def get_daily_trends(self, days: int = 30) -> List[Dict]:
        """Get daily trends"""
        trends = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days - 1 - i)
            date_key = date.strftime('%Y-%m-%d')
            
            stats = self.daily_stats.get(date_key, {
                'events': 0,
                'messages': 0,
                'sessions': 0,
                'errors': 0
            })
            
            trends.append({
                'date': date_key,
                **stats
            })
        
        return trends
    
    def get_error_analytics(self) -> Dict:
        """Get error analytics"""
        total_errors = sum(self.error_counts.values())
        
        error_data = []
        for error_type, count in sorted(self.error_counts.items(), key=lambda x: -x[1]):
            error_data.append({
                'error_type': error_type,
                'count': count,
                'percentage': round(count / max(total_errors, 1) * 100, 2)
            })
        
        return {
            'total_errors': total_errors,
            'errors': error_data[:10]  # Top 10 errors
        }
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
        if not self.response_times:
            return {
                'avg_response_time_ms': 0,
                'min_response_time_ms': 0,
                'max_response_time_ms': 0,
                'p50_response_time_ms': 0,
                'p95_response_time_ms': 0,
                'p99_response_time_ms': 0
            }
        
        sorted_times = sorted(self.response_times)
        
        return {
            'avg_response_time_ms': round(sum(sorted_times) / len(sorted_times) * 1000, 2),
            'min_response_time_ms': round(min(sorted_times) * 1000, 2),
            'max_response_time_ms': round(max(sorted_times) * 1000, 2),
            'p50_response_time_ms': round(sorted_times[len(sorted_times) // 2] * 1000, 2),
            'p95_response_time_ms': round(sorted_times[int(len(sorted_times) * 0.95)] * 1000, 2),
            'p99_response_time_ms': round(sorted_times[int(len(sorted_times) * 0.99)] * 1000, 2)
        }
    
    def get_full_report(self, period: str = '7d') -> Dict:
        """Get full analytics report"""
        return {
            'overview': self.get_overview(period),
            'skills': self.get_skill_analytics(),
            'hourly_distribution': self.get_hourly_distribution(),
            'daily_trends': self.get_daily_trends(),
            'errors': self.get_error_analytics(),
            'performance': self.get_performance_metrics(),
            'generated_at': datetime.now().isoformat()
        }
    
    def export_data(self, format: str = 'json') -> str:
        """Export analytics data"""
        data = {
            'events': [e.to_dict() for e in self.events[-1000:]],
            'skill_usage': dict(self.skill_usage),
            'error_counts': dict(self.error_counts),
            'daily_stats': self.daily_stats,
            'exported_at': datetime.now().isoformat()
        }
        
        if format == 'json':
            return json.dumps(data, ensure_ascii=False, indent=2)
        
        return str(data)


# Global instance
analytics_service = AnalyticsService()
