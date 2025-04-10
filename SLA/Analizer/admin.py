from django.contrib import admin
from .models import Subject,CustomUser,QuestionPaper,Question,Chat,ChatMessage
# Register your models here.

admin.site.register(Subject)
admin.site.register(CustomUser)
admin.site.register(QuestionPaper)
admin.site.register(Question)
admin.site.register(Chat)
admin.site.register(ChatMessage)
