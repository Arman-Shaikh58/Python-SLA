from django.contrib import admin
from .models import Subject,CustomUser,QuestionPaper
# Register your models here.

admin.site.register(Subject)
admin.site.register(CustomUser)
admin.site.register(QuestionPaper)
