from django.contrib import admin
from .models import ChatMessage

# Register your models here.
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_message', 'created_at')
    search_fields = ('user__username', 'user_message', 'bot_response')
    list_filter = ('created_at', 'user')