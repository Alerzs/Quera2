from rest_framework.permissions import BasePermission


class IsClassOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.is_owner(request.user)
    
class IsClassTeacherOrMentor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.is_teacher_or_mentor(request.user)