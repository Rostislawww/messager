from django.contrib import admin
from .models import Author, Message

# Реєстрація моделі Author
admin.site.register(Author)
admin.site.register(Message)