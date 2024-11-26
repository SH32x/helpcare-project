# dashboard/services/openai.py

from openai import AzureOpenAI
import os
import logging
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

class AIChatService:
    """
    Service class for managing chat interactions using Azure OpenAI GPT-4.
    """

    def __init__(self):
        """Initialize the Azure OpenAI client."""
        # Load environment variables
        load_dotenv()
        
        # Azure OpenAI Configuration
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.endpoint = "https://helpcareai4.openai.azure.com/"  
        
        if not self.api_key:
            raise ValueError("AZURE_OPENAI_KEY not found in environment variables")
        
        try:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version="2024-02-01",
                azure_endpoint=self.endpoint
            )
            logger.info("Successfully initialized Azure OpenAI client")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
            raise

        self.system_prompt = """You are a helpful assistant for a hospital. Your role is to:
        1. Answer questions about common hospital procedures and services
        2. Provide general medical information and guidance
        3. Explain hospital policies and protocols
        4. Direct patients to appropriate resources
        
        Always maintain a professional and compassionate tone. If asked about specific medical advice, 
        remind users to consult with healthcare professionals for personalized medical guidance."""

    def get_chat_response(self, user_prompt: str) -> str:
        """
        Generate an AI response using Azure OpenAI's GPT-4 model.
        """
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            logger.info(f"Sending request to Azure OpenAI endpoint: {self.endpoint}")
            
            # Get completion from Azure OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",  
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Get the response
            chat_response = response.choices[0].message.content
            logger.info("Successfully received response from Azure OpenAI")
            
            return chat_response
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            logger.error(f"Error in get_chat_response: {error_message}")
            return error_message