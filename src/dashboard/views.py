# dashboard/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services.openai import AIChatService
from models import Location
import json


def chat(request):
    """
    Renders the dedicated chat page
    """
    return render(request, 'dashboard/chat.html')


@csrf_exempt
def chat_message(request):
    """
    Handles chat messages and will interface with Azure AI services
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            
            # Initialize AI service and get response
            ai_service = AIChatService()
            response = ai_service.get_chat_response(message)
            
            return JsonResponse({
                'status': 'success',
                'response': response
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    })


