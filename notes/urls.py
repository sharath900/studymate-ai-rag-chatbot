from django.urls import path
from . import views


urlpatterns = [
    path('upload/', views.upload_notes, name='upload_notes'),
    path('chat/', views.study_chat, name='study_chat'),
    path('delete/<int:note_id>/', views.delete_note, name='delete_note'),
]