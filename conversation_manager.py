"""
Conversation Manager - Handles chat state and flow
"""
from typing import Dict, Optional, List, Tuple
from enum import Enum
import uuid
from datetime import datetime

class ConversationState(Enum):
    """States in the conversation flow"""
    INITIAL = "initial"
    AWAITING_AGE = "awaiting_age"
    AWAITING_LANGUAGE = "awaiting_language"
    READY = "ready"
    IN_CONVERSATION = "in_conversation"

class ConversationManager:
    """Manages conversation state and history"""
    
    def __init__(self):
        self.conversations: Dict[str, Dict] = {}
    
    def create_conversation(self, user_id: str = None) -> str:
        """Create a new conversation session"""
        if not user_id:
            user_id = str(uuid.uuid4())
        
        self.conversations[user_id] = {
            'user_id': user_id,
            'state': ConversationState.INITIAL,
            'age': None,
            'language': 'english',  # Default language
            'messages': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        return user_id
    
    def get_conversation(self, user_id: str) -> Optional[Dict]:
        """Get conversation by user_id"""
        return self.conversations.get(user_id)
    
    def set_age(self, user_id: str, age: str) -> bool:
        """Set age for a conversation"""
        if user_id not in self.conversations:
            return False
        
        # Validate age
        from config import Config
        if age not in Config.AGE_GROUPS:
            return False
        
        self.conversations[user_id]['age'] = age
        self.conversations[user_id]['updated_at'] = datetime.now().isoformat()
        
        # Update state
        if self.conversations[user_id]['state'] == ConversationState.AWAITING_AGE:
            if self.conversations[user_id]['language']:
                self.conversations[user_id]['state'] = ConversationState.READY
            else:
                self.conversations[user_id]['state'] = ConversationState.AWAITING_LANGUAGE
        
        return True
    
    def set_language(self, user_id: str, language: str) -> bool:
        """Set language for a conversation"""
        if user_id not in self.conversations:
            return False
        
        # Validate language
        from config import Config
        if language.lower() not in Config.SUPPORTED_LANGUAGES:
            return False
        
        self.conversations[user_id]['language'] = language.lower()
        self.conversations[user_id]['updated_at'] = datetime.now().isoformat()
        
        # Update state
        if self.conversations[user_id]['state'] == ConversationState.AWAITING_LANGUAGE:
            if self.conversations[user_id]['age']:
                self.conversations[user_id]['state'] = ConversationState.READY
            else:
                self.conversations[user_id]['state'] = ConversationState.AWAITING_AGE
        
        return True

    def translate_conversation(self, user_id: str, target_language: str, translator) -> bool:
        """Translate all messages in a conversation to target_language using provided translator

        The translator is expected to be a callable that accepts a list of messages and a target language
        and returns a list of translated contents in the same order.
        """
        if user_id not in self.conversations:
            return False

        messages = self.conversations[user_id]['messages']
        if not messages:
            return True

        try:
            translated = translator(messages, target_language)
            # translated should be a list of strings matching messages order
            if not translated or len(translated) != len(messages):
                return False

            for i, m in enumerate(messages):
                m['content'] = translated[i]

            self.conversations[user_id]['updated_at'] = datetime.now().isoformat()
            return True
        except Exception:
            return False
    
    def add_message(self, user_id: str, role: str, content: str):
        """Add a message to conversation history"""
        if user_id not in self.conversations:
            return
        
        self.conversations[user_id]['messages'].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        self.conversations[user_id]['updated_at'] = datetime.now().isoformat()
        
        if self.conversations[user_id]['state'] == ConversationState.READY:
            self.conversations[user_id]['state'] = ConversationState.IN_CONVERSATION
    
    def can_process_symptoms(self, user_id: str) -> Tuple[bool, str]:
        """Check if conversation is ready to process symptoms"""
        if user_id not in self.conversations:
            return False, "Conversation not found"
        
        conv = self.conversations[user_id]
        
        if not conv['age']:
            return False, "Age selection is required before processing symptoms"
        
        if not conv['language']:
            return False, "Language selection is required"
        
        return True, "Ready"
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        if user_id not in self.conversations:
            return []
        
        messages = self.conversations[user_id]['messages']
        return messages[-limit:] if limit else messages
    
    def cleanup_old_conversations(self, max_age_hours: int = 24):
        """Clean up old conversations (optional maintenance)"""
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for user_id, conv in self.conversations.items():
            updated = datetime.fromisoformat(conv['updated_at'])
            if updated < cutoff:
                to_remove.append(user_id)
        
        for user_id in to_remove:
            del self.conversations[user_id]

# Global conversation manager instance
conversation_manager = ConversationManager()

