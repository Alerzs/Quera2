from django.contrib import admin
from .models import *


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('participents',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'room', 'text', 'send_time')
    search_fields = ('text', 'sender__username', 'room__name')
    list_filter = ('send_time',)


@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    list_display = ('name', 'shenase', 'capacity', 'permision', 'join_time')
    search_fields = ('name', 'shenase')
    list_filter = ('permision',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('soal', 'deadline', 'send_limit', 'mark', 'late_penalty')
    list_filter = ('deadline',)


@admin.register(Scores)
class ScoresAdmin(admin.ModelAdmin):
    list_display = ('question', 'student', 'taken_mark')
    search_fields = ('student__username', 'question__soal__name')


@admin.register(Team)
class GroupsAdmin(admin.ModelAdmin):
    list_display = ('id',)
    filter_horizontal = ('members',)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'contribution_type', 'marking_type')
    filter_horizontal = ('teams', 'questions')


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ('target_class', 'reciver', 'invite_id')
    search_fields = ('invite_id', 'reciver__username', 'target_class__name')

@admin.register(ClassRoles)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'kelas', 'role')

