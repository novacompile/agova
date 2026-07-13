"""Context and memory management for agents"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class ContextManager:
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
        self.current_session: Optional[str] = None
    
    def create_session(self, prompt: str) -> str:
        """Create a new session"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.sessions[session_id] = [{
            "timestamp": datetime.now().isoformat(),
            "type": "prompt",
            "content": prompt
        }]
        self.current_session = session_id
        return session_id
    
    def add_message(self, agent: str, message: Dict[str, Any]):
        """Add a message to the current session"""
        if self.current_session and self.current_session in self.sessions:
            self.sessions[self.current_session].append({
                "timestamp": datetime.now().isoformat(),
                "agent": agent,
                "content": message
            })
            
            # Trim history if needed
            if len(self.sessions[self.current_session]) > self.max_history:
                self.sessions[self.current_session] = self.sessions[self.current_session][-self.max_history:]
    
    def get_context(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get context for a session"""
        sid = session_id or self.current_session
        return self.sessions.get(sid, [])
    
    def get_last_n_messages(self, n: int = 5, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get last n messages from a session"""
        context = self.get_context(session_id)
        return context[-n:] if context else []
    
    def summarize_context(self, session_id: Optional[str] = None) -> str:
        """Get a summary of the session context"""
        context = self.get_context(session_id)
        if not context:
            return "No context available"
        
        summary = {
            "session_id": session_id or self.current_session,
            "total_messages": len(context),
            "first_message": context[0] if context else None,
            "last_message": context[-1] if context else None,
            "agents_involved": list(set(
                msg.get("agent", "user") for msg in context
            )),
            "duration": "N/A"
        }
        
        # Calculate duration if we have timestamps
        if len(context) >= 2 and "timestamp" in context[0] and "timestamp" in context[-1]:
            try:
                start = datetime.fromisoformat(context[0]["timestamp"])
                end = datetime.fromisoformat(context[-1]["timestamp"])
                summary["duration"] = str(end - start)
            except:
                pass
        
        return json.dumps(summary, indent=2)
    
    def clear_session(self, session_id: Optional[str] = None):
        """Clear a session's context"""
        sid = session_id or self.current_session
        if sid in self.sessions:
            del self.sessions[sid]
    
    def list_sessions(self) -> List[str]:
        """List all session IDs"""
        return list(self.sessions.keys())
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a specific session"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        context = self.sessions[session_id]
        return {
            "session_id": session_id,
            "message_count": len(context),
            "created_at": context[0]["timestamp"] if context else None,
            "last_updated": context[-1]["timestamp"] if context else None
        }
