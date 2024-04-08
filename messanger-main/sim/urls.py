from django.urls import path
from . import views

urlpatterns = [
    path('', views.register, name='register'),
    path('accounts/login/', views.register, name='register'),
    path('redirect-to-register/', views.redirect_to_register, name='redirect_to_register'),
    path('lobby/', views.lobby, name='lobby'),
    path('login/', views.login, name='login'),
    path('chat/', views.chat, name='chat'),
    path('chat/<str:chat_id>/', views.chat, name='chat'),
    path('create-message/', views.create_message, name='create-message'),
    path('stream-chat-messages/<str:chat_id>/', views.stream_chat_messages, name='stream-chat-messages'),
    path('delete-message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('edit-message/<int:message_id>/', views.edit_message, name='edit_message'),
]
