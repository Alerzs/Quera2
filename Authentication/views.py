from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .models import QueraUser
from rest_framework.response import Response
from rest_framework import status


class Login(TokenObtainPairView):
    pass

class Refresh(TokenRefreshView):
    pass

class Register(APIView):
    def post(self ,request):
        name = request.data.get('name')
        username = request.data.get('username')
        password = request.data.get('password')
        phone = request.data.get('phone')
        email = request.data.get('email')
        if not name or not username or not password:
            raise ValidationError('name , username , password ,phone and email is required')

        QueraUser.objects.create(name=name, username=username ,password=password ,email=email ,phone=phone)
        return Response("you registered successfully" ,status=status.HTTP_201_CREATED)