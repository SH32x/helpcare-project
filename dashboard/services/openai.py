# dashboard/services/openai.py

from openai import AzureOpenAI
import os
from ..models import ChatMessage
from datetime import datetime, timedelta

class AIChatService:
    """
    Simple service class for managing chat interactions using Azure OpenAI GPT-4.
    Handles basic rate limiting for a single user chat session.
    """

    def __init__(self):
        """Initialize the Azure OpenAI client and rate limiting variables."""
        self.client = AzureOpenAI(
            azure_endpoint="https://helpcareai4.openai.azure.com/",
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01"
        )
        
        # Simple rate limiting tracking
        self.last_request_time = None
        self.requests_in_last_minute = 0
        self.tokens_in_last_minute = 0
        self.last_minute_start = datetime.now()
        
        self.system_prompt = """You are a helpful assistant for a hospital. Your role is to:
        1. Answer questions about common hospital procedures and services
        2. Provide general medical information and guidance
        3. Explain hospital policies and protocols
        4. Direct patients to appropriate resources
        
        Always maintain a professional and compassionate tone. If asked about specific medical advice, 
        remind users to consult with healthcare professionals for personalized medical guidance."""

    def _check_rate_limits(self) -> tuple[bool, str]:
        """
        Check if we're within rate limits.
        Returns (can_proceed, error_message)
        """
        current_time = datetime.now()
        
        # Reset counters if a minute has passed
        if self.last_minute_start and (current_time - self.last_minute_start) >= timedelta(minutes=1):
            self.requests_in_last_minute = 0
            self.tokens_in_last_minute = 0
            self.last_minute_start = current_time
            
        # Check request rate limit (6 per minute)
        if self.requests_in_last_minute >= 6:
            return False, "Please wait a moment before sending another message. (Rate limit: 6 requests per minute)"
            
        # Check token rate limit (1000 per minute)
        if self.tokens_in_last_minute >= 1000:
            return False, "Please wait a moment before sending another message. (Rate limit: 1000 tokens per minute)"
            
        return True, ""

    def get_chat_response(self, user_prompt: str, include_history: bool = True) -> str:
        """
        Generate an AI response using Azure OpenAI's GPT-4 model.
        
        Args:
            user_prompt (str): The incoming message from the user
            include_history (bool): Whether to include recent chat history
        
        Returns:
            str: The AI-generated response
        """
        try:
            # Check rate limits
            can_proceed, error_message = self._check_rate_limits()
            if not can_proceed:
                return error_message
                
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Include recent chat history if enabled
            if include_history:
                recent_messages = ChatMessage.objects.order_by('-timestamp')[:5]
                for msg in reversed(recent_messages):
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # Add current user message
            messages.append({"role": "user", "content": user_prompt})
            
            # Get completion from Azure OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
            )
            
            # Update rate limiting counters
            self.requests_in_last_minute += 1
            self.tokens_in_last_minute += response.usage.total_tokens
            self.last_request_time = datetime.now()
            
            # Get and save the response
            chat_response = response.choices[0].message.content
            
            # Save conversation to database
            ChatMessage.objects.create(role="user", content=user_prompt)
            ChatMessage.objects.create(role="assistant", content=chat_response)
            
            return chat_response
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            ChatMessage.objects.create(role="assistant", content=error_message)
            return error_message