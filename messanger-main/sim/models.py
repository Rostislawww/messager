# models.py
from django import forms
from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=500)

from django.db import models

class Chat(models.Model):
    chat_name = models.CharField(max_length=100)
    participants = models.CharField(max_length=1000)

class Message(models.Model):
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)






    