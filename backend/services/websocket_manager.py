"""
WebSocket Manager Service
Real-time notifications and updates
"""

from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket
from datetime import datetime
import json
import asyncio


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates
    """
    
    def __init__(self):
        # Active connections by session
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
        # Admin connections for system-wide updates
        self.admin_connections: Set[WebSocket] = set()
        
        # Global broadcast connections
        self.broadcast_connections: Set[WebSocket] = set()
        
        # Connection metadata
        self.connection_info: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if session_id:
            if session_id not in self.active_connections:
                self.active_connections[session_id] = []
            self.active_connections[session_id].append(websocket)
            
            self.connection_info[id(websocket)] = {
                'session_id': session_id,
                'connected_at': datetime.now().isoformat(),
                'type': 'session'
            }
        else:
            self.broadcast_connections.add(websocket)
            self.connection_info[id(websocket)] = {
                'connected_at': datetime.now().isoformat(),
                'type': 'broadcast'
            }
        
        # Notify admins about new connection
        await self.notify_admins({
            'type': 'connection',
            'action': 'connected',
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
    
    async def connect_admin(self, websocket: WebSocket):
        """Connect an admin WebSocket"""
        await websocket.accept()
        self.admin_connections.add(websocket)
        
        self.connection_info[id(websocket)] = {
            'connected_at': datetime.now().isoformat(),
            'type': 'admin'
        }
        
        # Send current stats
        await self.send_personal_message(websocket, {
            'type': 'welcome',
            'message': 'Connected to admin notifications',
            'active_sessions': len(self.active_connections),
            'active_connections': sum(len(c) for c in self.active_connections.values())
        })
    
    def disconnect(self, websocket: WebSocket, session_id: str = None):
        """Handle WebSocket disconnection"""
        
        # Remove from session connections
        if session_id and session_id in self.active_connections:
            try:
                self.active_connections[session_id].remove(websocket)
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
            except ValueError:
                pass
        
        # Remove from broadcast connections
        self.broadcast_connections.discard(websocket)
        
        # Remove from admin connections
        self.admin_connections.discard(websocket)
        
        # Remove metadata
        if id(websocket) in self.connection_info:
            del self.connection_info[id(websocket)]
    
    async def send_personal_message(self, websocket: WebSocket, message: Dict):
        """Send a message to a specific WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
    
    async def send_to_session(self, session_id: str, message: Dict):
        """Send a message to all connections in a session"""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending to session {session_id}: {e}")
    
    async def broadcast(self, message: Dict):
        """Broadcast a message to all connections"""
        all_connections = list(self.broadcast_connections)
        for connections in self.active_connections.values():
            all_connections.extend(connections)
        
        for connection in all_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting: {e}")
    
    async def notify_admins(self, message: Dict):
        """Send notification to all admin connections"""
        disconnected = []
        
        for connection in self.admin_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected admins
        for connection in disconnected:
            self.admin_connections.discard(connection)
    
    async def notify_typing(self, session_id: str, is_typing: bool):
        """Notify about typing status"""
        await self.send_to_session(session_id, {
            'type': 'typing',
            'is_typing': is_typing,
            'timestamp': datetime.now().isoformat()
        })
    
    async def notify_message(self, session_id: str, message: Dict):
        """Notify about new message"""
        await self.send_to_session(session_id, {
            'type': 'message',
            'data': message,
            'timestamp': datetime.now().isoformat()
        })
    
    async def notify_skill_activated(self, session_id: str, skill_name: str):
        """Notify about skill activation"""
        await self.send_to_session(session_id, {
            'type': 'skill_activated',
            'skill': skill_name,
            'timestamp': datetime.now().isoformat()
        })
    
    async def notify_system_update(self, update_type: str, data: Dict = None):
        """Notify about system updates"""
        message = {
            'type': 'system_update',
            'update_type': update_type,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }
        
        await self.broadcast(message)
        await self.notify_admins(message)
    
    def get_connection_stats(self) -> Dict:
        """Get connection statistics"""
        return {
            'total_sessions': len(self.active_connections),
            'total_connections': sum(len(c) for c in self.active_connections.values()),
            'admin_connections': len(self.admin_connections),
            'broadcast_connections': len(self.broadcast_connections)
        }
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.active_connections.keys())


class NotificationService:
    """
    High-level notification service
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
        self.notification_queue: List[Dict] = []
    
    async def send_notification(
        self,
        title: str,
        message: str,
        notification_type: str = 'info',
        session_id: str = None,
        data: Dict = None
    ):
        """Send a notification"""
        notification = {
            'type': 'notification',
            'notification_type': notification_type,
            'title': title,
            'message': message,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }
        
        if session_id:
            await self.manager.send_to_session(session_id, notification)
        else:
            await self.manager.broadcast(notification)
        
        # Store in queue
        self.notification_queue.append(notification)
        if len(self.notification_queue) > 100:
            self.notification_queue = self.notification_queue[-50:]
    
    async def send_alert(self, message: str, level: str = 'warning'):
        """Send an alert to all admins"""
        await self.manager.notify_admins({
            'type': 'alert',
            'level': level,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    async def send_progress(self, session_id: str, progress: int, message: str = None):
        """Send progress update"""
        await self.manager.send_to_session(session_id, {
            'type': 'progress',
            'progress': progress,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_recent_notifications(self, limit: int = 10) -> List[Dict]:
        """Get recent notifications"""
        return self.notification_queue[-limit:]


# Global instances
connection_manager = ConnectionManager()
notification_service = NotificationService(connection_manager)
