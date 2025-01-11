from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import QueraUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = QueraUser
        fields = ('username','name', 'email', 'phone') 

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = QueraUser
        fields = ('username','name', 'email', 'phone')