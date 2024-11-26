# dashboard/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services.openai import AIChatService
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

def chat(request):
    """Renders the chat page"""
    return render(request, 'dashboard/chat.html')

@csrf_exempt
def chat_message(request):
    """Handles chat messages and interfaces with Azure OpenAI"""
    if request.method == 'POST':
        try:
            # Log the incoming request
            logger.info("Received chat message request")
            
            # Parse the request body
            data = json.loads(request.body)
            message = data.get('message', '')
            
            if not message:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No message provided'
                }, status=400)
            
            logger.info(f"Processing message: {message[:50]}...")
            
            # Initialize AI service and get response
            ai_service = AIChatService()
            response = ai_service.get_chat_response(message)
            
            logger.info("AI response success.")
            
            return JsonResponse({
                'status': 'success',
                'response': response
            })
            
        except Exception as e:
            logger.error(f"Error in chat_message view: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)