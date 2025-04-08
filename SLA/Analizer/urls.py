from . import views
from django.urls import path

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.User_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.User_register, name='register'),
    path('add_subject/', views.add_subject, name='add_subject'),
    path('subject_info/<int:subject_id>/', views.subject_info, name='subject_info'),
    path('subject_info/<int:subject_id>/upload/', views.upload_question_paper, name='upload_question_paper'),
    path('subjects/', views.subjects, name='subjects'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/start/', views.start_chat, name='start_chat'),
    path('chat/send/', views.send_message, name='send_message'),
    path('chat/messages/', views.get_chat_messages, name='get_chat_messages'),
]
