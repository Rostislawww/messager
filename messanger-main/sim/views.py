
import asyncio
from asgiref.sync import sync_to_async

from typing import AsyncGenerator
from . import models
import json
import random
import uuid
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, StreamingHttpResponse, HttpResponse, HttpResponseServerError
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login
from django.db.models import Q
from .forms import ChatCreateForm, RegistrationForm
from .models import Chat, Message, Author


from sim import models


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                request.session['username'] = username
                return redirect('lobby')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('register')

@login_required
def lobby(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        chat_id = request.POST.get('chat_id')
        if chat_id:
            request.session['chat_id'] = chat_id
        else:
            return render(request, 'lobby.html',)
        return redirect('chat', chat_id=request.session['chat_id'])
    else:
        return render(request, 'lobby.html')

@login_required
def chat(request: HttpRequest, chat_id: str = None) -> HttpResponse:
    request.session['chat_id'] = chat_id
    if not request.user.is_authenticated or not chat_id:
        return redirect('register')  # Перенаправлення на сторінку реєстрації
    return render(request, 'chat.html', {'chat_id': chat_id})


@login_required
def redirect_to_register(request):
    return redirect('register')
def create_message(request: HttpRequest) -> HttpResponse:
    content = request.POST.get("content")
    username = request.session.get("username")
    chat_id = request.session.get("chat_id")

    if not username or not chat_id:
        return HttpResponse(status=403)
    author, _ = models.Author.objects.get_or_create(name=username)

    if content:
        models.Message.objects.create(author=author, content=content, chat_id=chat_id)
        return HttpResponse(status=201)
    else:
        return HttpResponse(status=200)

async def stream_chat_messages(request: HttpRequest, chat_id: str) -> StreamingHttpResponse:
    """
    Streams chat messages to the client as we create messages.
    """
    async def event_stream():
        """
        We use this function to send a continuous stream of data
        to the connected clients.
        """
        async for message in get_existing_messages(chat_id):
            yield message

        last_id = await get_last_message_id()

        while True:
            new_messages = models.Message.objects.filter(id__gt=last_id, chat_id=chat_id).order_by('created_at').values(
                'id', 'author__name', 'content'
            )
            async for message in new_messages:
                yield f"data: {json.dumps(message)}\n\n"
                last_id = message['id']
            await asyncio.sleep(0.1)  # Adjust sleep time as needed to reduce db queries.

    async def get_existing_messages(chat_id) -> AsyncGenerator:
        messages = models.Message.objects.filter(chat_id=chat_id).order_by('created_at').values(
            'id', 'author__name', 'content'
        )
        async for message in messages:
            yield f"data: {json.dumps(message)}\n\n"

    async def get_last_message_id() -> int:
        last_message = await sync_to_async(models.Message.objects.filter(chat_id=chat_id).last)()
        return last_message.id if last_message else 0

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')



def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    if str(request.user) == str(message.author.name):
        message.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})


def edit_message(request, message_id):
    if request.method == 'PUT':
        content = json.loads(request.body.decode('utf-8'))['content']
        message = get_object_or_404(Message, id=message_id)
        
        if str(request.user) == str(message.author.name):
            message.content = content
            message.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'You are not the author of this message'})
    else:
        return JsonResponse({'success': False, 'message': 'Method not allowed'})
