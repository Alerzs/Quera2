from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin
from .models import QueraUser
from .forms import CustomUserCreationForm, CustomUserChangeForm



@register(QueraUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = QueraUser

    list_display = ['username','name', 'email', 'phone', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone','name')}), 
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone','name')}),  
    )
