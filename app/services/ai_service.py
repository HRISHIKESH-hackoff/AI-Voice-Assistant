"""AI Service - Integration with OpenAI and Perplexity API."""
import logging
import os
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class AIService:
    """Handle AI-powered responses using OpenAI or Perplexity API."""

    def __init__(self):
        """Initialize AI service with API keys."""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        self.ai_provider = 'perplexity'  # Default to Perplexity
        logger.info('AIService initialized')

    def get_response(self, user_message: str, max_tokens: int = 500) -> Optional[str]:
        """Get AI response for user message.
        
        Args:
            user_message: User's input message
            max_tokens: Maximum tokens in response
            
        Returns:
            AI response text or None if API call fails
        """
        try:
            if self.ai_provider == 'perplexity' and self.perplexity_api_key:
                return self._get_perplexity_response(user_message, max_tokens)
            elif self.openai_api_key:
                return self._get_openai_response(user_message, max_tokens)
            else:
                return self._get_fallback_response(user_message)
                
        except Exception as e:
            logger.error(f'Error getting AI response: {str(e)}')
            return None

    def _get_perplexity_response(self, user_message: str, max_tokens: int) -> Optional[str]:
        """Get response from Perplexity API."""
        try:
            headers = {
                'Authorization': f'Bearer {self.perplexity_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'pplx-7b-online',
                'messages': [{'role': 'user', 'content': user_message}],
                'max_tokens': max_tokens
            }
            
            response = requests.post(
                'https://api.perplexity.ai/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                logger.error(f'Perplexity API error: {response.status_code}')
                return None
                
        except Exception as e:
            logger.error(f'Perplexity API error: {str(e)}')
            return None

    def _get_openai_response(self, user_message: str, max_tokens: int) -> Optional[str]:
        """Get response from OpenAI API."""
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[{'role': 'user', 'content': user_message}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f'OpenAI API error: {str(e)}')
            return None

    def _get_fallback_response(self, user_message: str) -> str:
        """Provide fallback response when APIs are not configured."""
        logger.warning('No AI API configured, using fallback response')
        
        # Simple pattern-based fallback responses
        message_lower = user_message.lower()
        
        if 'hello' in message_lower or 'hi' in message_lower:
            return 'Hello! How can I assist you today?'
        elif 'how are you' in message_lower:
            return 'I am functioning well. Thank you for asking!'
        elif 'weather' in message_lower:
            return 'I would need API access to check current weather conditions.'
        elif 'time' in message_lower:
            from datetime import datetime
            return f'The current time is {datetime.now().strftime("%H:%M:%S")}.'
        else:
            return 'I understand you said: "' + user_message + '". Please configure an AI API to get more detailed responses.'

    def set_ai_provider(self, provider: str) -> None:
        """Set the AI provider (perplexity or openai).
        
        Args:
            provider: 'perplexity' or 'openai'
        """
        if provider in ['perplexity', 'openai']:
            self.ai_provider = provider
            logger.info(f'AI provider set to: {provider}')
        else:
            logger.warning(f'Invalid AI provider: {provider}')

    def test_connection(self) -> bool:
        """Test API connection.
        
        Returns:
            True if API is reachable, False otherwise
        """
        try:
            test_response = self.get_response('Hello', max_tokens=10)
            return test_response is not None
        except Exception as e:
            logger.error(f'Connection test failed: {str(e)}')
            return False
