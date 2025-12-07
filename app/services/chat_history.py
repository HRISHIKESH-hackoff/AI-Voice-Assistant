"""Chat History Manager - Message storage and retrieval."""
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ChatHistory:
    """Manage conversation history."""

    def __init__(self, max_messages: int = 100):
        """Initialize chat history.
        
        Args:
            max_messages: Maximum messages to store (default: 100)
        """
        self.messages: List[Dict] = []
        self.max_messages = max_messages
        logger.info(f'ChatHistory initialized with max {max_messages} messages')

    def add_message(self, user_message: str, ai_response: str) -> Dict:
        """Add a message pair to history.
        
        Args:
            user_message: User's input
            ai_response: AI's response
            
        Returns:
            Message object added to history
        """
        message_obj = {
            'id': len(self.messages) + 1,
            'timestamp': datetime.now().isoformat(),
            'user': user_message,
            'assistant': ai_response,
            'duration': 0  # Can be populated with actual duration
        }
        
        self.messages.append(message_obj)
        
        # Maintain max message limit
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)  # Remove oldest message
            
        logger.info(f'Message added. Total messages: {len(self.messages)}')
        return message_obj

    def get_last_message(self) -> Optional[Dict]:
        """Get the last message pair.
        
        Returns:
            Last message or None if history is empty
        """
        return self.messages[-1] if self.messages else None

    def get_last_timestamp(self) -> Optional[str]:
        """Get timestamp of last message.
        
        Returns:
            Timestamp string or None
        """
        last = self.get_last_message()
        return last['timestamp'] if last else None

    def get_all_messages(self) -> List[Dict]:
        """Get all messages in history.
        
        Returns:
            List of all message objects
        """
        return self.messages.copy()

    def get_messages(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Get paginated messages.
        
        Args:
            limit: Number of messages to return
            offset: Starting position
            
        Returns:
            List of message objects
        """
        return self.messages[offset:offset+limit]

    def search_messages(self, query: str) -> List[Dict]:
        """Search messages by keyword.
        
        Args:
            query: Search term
            
        Returns:
            List of matching messages
        """
        results = []
        query_lower = query.lower()
        
        for msg in self.messages:
            if (query_lower in msg['user'].lower() or 
                query_lower in msg['assistant'].lower()):
                results.append(msg)
                
        logger.info(f'Found {len(results)} messages matching \"{query}\"')
        return results

    def clear(self) -> None:
        """Clear all messages from history."""
        count = len(self.messages)
        self.messages.clear()
        logger.info(f'Chat history cleared. Deleted {count} messages')

    def delete_message(self, message_id: int) -> bool:
        """Delete a specific message.
        
        Args:
            message_id: ID of message to delete
            
        Returns:
            True if deleted, False if not found
        """
        for i, msg in enumerate(self.messages):
            if msg['id'] == message_id:
                self.messages.pop(i)
                logger.info(f'Message {message_id} deleted')
                return True
        return False

    def get_conversation_summary(self) -> Dict:
        """Get summary statistics of chat history.
        
        Returns:
            Dictionary with summary information
        """
        if not self.messages:
            return {'total_messages': 0, 'avg_response_length': 0}
            
        total_messages = len(self.messages)
        total_response_length = sum(len(m['assistant']) for m in self.messages)
        avg_response_length = total_response_length // total_messages if total_messages > 0 else 0
        
        return {
            'total_messages': total_messages,
            'avg_response_length': avg_response_length,
            'first_message': self.messages[0]['timestamp'],
            'last_message': self.messages[-1]['timestamp']
        }
