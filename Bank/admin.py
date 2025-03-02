from django.contrib import admin
from .models import Soal ,SubmitedAnswer

@admin.register(Soal)
class SoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'category', 'level', 'answer_type')


@admin.register(SubmitedAnswer)
class SubmitedAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'soal', 'result')
    list_filter = ('soal__answer_type', 'user')
    search_fields = ('user__username', 'soal__name')
    readonly_fields = ('result',)