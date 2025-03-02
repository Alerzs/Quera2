from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .models import QueraUser
from .serializers import *
from rest_framework.response import Response
from rest_framework import status


class Login(TokenObtainPairView):
    pass

class Refresh(TokenRefreshView):
    pass

class Register(APIView):
    queryset = QueraUser.objects.all()
    serializer = QUSerializer