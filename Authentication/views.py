from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView
from rest_framework import generics
from .models import QueraUser
from .serializers import *


class Login(TokenObtainPairView):
    pass

class Refresh(TokenRefreshView):
    pass

class Register(generics.CreateAPIView):
    queryset = QueraUser.objects.all()
    serializer_class = QUSerializer