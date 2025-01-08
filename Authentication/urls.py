from django.urls import path
from .views import Login ,Register ,Refresh

urlpatterns = [
    path('login/' ,Login.as_view()),
    path('register/' ,Register.as_view()),
    path('refresh/' ,Refresh.as_view())
]