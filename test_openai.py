# test_openai.py

import os
from dotenv import load_dotenv
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_openai_connection():
    """Test the OpenAI connection with detailed logging"""
    try:
        # Log environment check
        logger.info("Checking environment variables...")
        api_key = os.getenv("AZURE_OPENAI_KEY")
        logger.info(f"API key present: {bool(api_key)}")
        
        from dashboard.services.openai import AIChatService
        
        logger.info("Creating AIChatService instance...")
        service = AIChatService()
        
        test_message = "Hello, what services does this hospital provide?"
        logger.info(f"Sending test message: {test_message}")
        
        response = service.get_chat_response(test_message)
        
        logger.info("Response received:")
        print("\nAI Response:", response)
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        raise

if __name__ == "__main__":
    load_dotenv()
    test_openai_connection()