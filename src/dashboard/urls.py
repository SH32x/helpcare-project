# dashboard/urls.py
from django.urls import path
from dashboard import views

urlpatterns = [
    path('', views.chat, name='chat'),
    path('api/chat-message/', views.chat_message, name='chat_message'),
]