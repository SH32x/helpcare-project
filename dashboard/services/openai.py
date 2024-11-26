# dashboard/services/openai.py

from openai import AzureOpenAI
from django.conf import settings
import os
from ..models import ChatMessage

class AIChatService:
    """
    Service class for managing hospital-related AI interactions using Azure OpenAI.
    
    This class handles:
    - OpenAI client configuration
    - Chat message processing
    - Response generation
    - Conversation history management
    
    Attributes:
        client: OpenAI client instance
        system_prompt: Base prompt defining AI behavior
    """

    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-02-01"
        )
        

        self.system_prompt = """You are a helpful assistant for a hospital. Your role is to:
        1. Answer questions about common hospital procedures and services
        2. Provide general medical information and guidance
        3. Explain hospital policies and protocols
        4. Direct patients to appropriate resources
        
        Always maintain a professional and compassionate tone. If asked about specific medical advice, 
        remind users to consult with healthcare professionals for personalized medical guidance."""

    def get_chat_response(self, user_prompt: str, include_history: bool = True) -> str:
        """
        Generate an AI response to a user message using Azure OpenAI.
        
        Args:
            user_prompt (str): The incoming message from the user
            include_history (bool): Whether to include recent chat history for context
        
        Returns:
            str: The AI-generated response
            
        Configuration Notes:
            - temperature: Controls randomness (0.0-1.0)
                0.0 = More focused, consistent responses
                0.7 = Balanced creativity and consistency
                1.0 = Maximum creativity
            - max_tokens: Limits response length
                800 = Roughly 600 words
                Adjust based on your needs (higher = longer responses)
        """
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Include recent chat history if enabled
            if include_history:
                # Retrieve last 5 messages for context
                # Adjust the number based on your needs and token limits
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
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT'),
                messages=messages,
                temperature=0.7,  
                max_tokens=600,   
                
            )
            
            chat_response = response.choices[0].message.content
            
            # Save the conversation to the database for history
            ChatMessage.objects.create(role="user", content=user_prompt)
            ChatMessage.objects.create(role="assistant", content=chat_response)
            
            return chat_response
            
        except Exception as e:
            ex = f"An error has occurred: {str(e)}"
            ChatMessage.objects.create(role="assistant", content=ex)
            return ex