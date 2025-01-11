from .models import *
from Bank.models import *
from Authentication.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from .serializers import *


class Classview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self ,request):
        my_user = request.user
        name = request.data.get('name')
        description = request.data.get('description')
        capacity = request.data.get('capacity')
        permision = request.data.get('permision')
        password = request.data.get('password')
        join_time = request.data.get('join_time')

        if not name and not permision:
            return Response({'required':['name','permision'] ,'optional':['description','capacity','password','join_time']},status=status.HTTP_400_BAD_REQUEST)
        my_forum = Forum.objects.create(name = f"{name} forum")
        my_forum.participents.add(my_user)
        my_class = Classes.objects.create(name=name,description=description,shenase=get_random_string(20),capacity=capacity,
                           permision=permision,password=password,join_time=join_time,forum=my_forum)
        ClassRoles.objects.create(user=my_user, kelas=my_class, role='O')
        my_forum.save()
        return Response({'detail': 'Class created successfully'}, status=status.HTTP_201_CREATED)

    def get(self ,request):
        my_user = request.user
        classes = Classes.objects.filter(classroles__user = my_user)
        serializer = ClassSerializer(classes ,many=True)
        return Response(serializer.data ,status=status.HTTP_200_OK)
    

class ClassDetail(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, shenase):
        my_user = request.user
        my_class = get_object_or_404(Classes ,shenase=shenase ,classroles__user = my_user)
        serializer = ClassSerializer(my_class, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request ,shenase):
        my_user = request.user
        my_class = get_object_or_404(Classes ,shenase=shenase ,classroles__user = my_user)
        serializer = ClassSerializer(my_class)
        return Response(serializer.data , status=status.HTTP_200_OK)


class JoinClass(APIView):
    permission_classes = [IsAuthenticated]
    def get(self ,request ,shenase):
        my_user = request.user
        try:
            my_class = Classes.objects.get(shenase=shenase)
        except:
            return Response('class not found' ,status=status.HTTP_404_NOT_FOUND)
        if my_class.permision == 'pri':
            return Response('this class is private' ,status=status.HTTP_403_FORBIDDEN)
        if ClassRoles.objects.filter(kelas=my_class ,user=my_user).exists():
            return Response('you are already in this class' ,status=status.HTTP_403_FORBIDDEN)
        my_class.forum.participents.add(my_user)

        ClassRoles.objects.create(kelas=my_class ,user=my_user ,role='S')
        my_class.save()

        return Response('you joined the class successfully' ,status=status.HTTP_200_OK)

    def post(self ,request ,shenase):
        my_user = request.user
        password = request.data.get('password')
        if not password:
            return Response('password is required' ,status=status.HTTP_403_FORBIDDEN)
        try:
            my_class = Classes.objects.get(shenase=shenase)
        except:
            return Response('class not found' ,status=status.HTTP_404_NOT_FOUND)
        if my_class.permision == 'pub':
            return Response('post method is not allowed' ,status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if my_class.password != password:
            return Response('wrong password' ,status=status.HTTP_403_FORBIDDEN)

        my_forum = my_class.forum
        my_forum.participents.add(my_user)

        ClassRoles.objects.create(kelas=my_class ,user=my_user ,role='S')
        my_forum.save()
        return Response('you joined the class successfully' ,status=status.HTTP_200_OK)
        
         
class JoinClassByInvitation(APIView):
    permission_classes = [IsAuthenticated]

    def get(self ,request ,invite_id):
        my_user = request.user
        try:
            my_invite = Invite.objects.get(invite_id=invite_id)
        except:
            return Response('invite id is wrong or expired' ,status=status.HTTP_404_NOT_FOUND)
        if my_invite.reciver != my_user:
            return Response('this link is not valid on your account' ,status=status.HTTP_403_FORBIDDEN)
        my_class = my_invite.target_class
        my_forum = my_class.forum
        my_forum.participents.add(my_user)    
        ClassRoles.objects.create(kelas=my_class ,user=my_user ,role='S')
        my_forum.save()
        my_invite.delete()
        return Response('you joined the class successfully' ,status=status.HTTP_200_OK)

class SendInvitation(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request ,shenase):
        username_list = request.data.get('username_list')
        my_user = request.user
        my_class = get_object_or_404(Classes ,shenase=shenase)
        if not ClassRoles.objects.filter(kelas=my_class ,user=my_user ,role='O').exists():
            return Response("you dont have permision on this class" ,status=status.HTTP_403_FORBIDDEN)
        if not username_list:
            return Response('username_list field is required' ,status=status.HTTP_403_FORBIDDEN)
        error_log = []
        for item in username_list:
            try:
                user = QueraUser.objects.get(username=item)
            except:
                error_log.append({'user_not_found':{item}})
                continue
            invite_id = get_random_string(20)
            Invite.objects.create(reciver=user,target_class=my_class,invite_id=invite_id)
            email_text = 'http//:127.0.0.1/private/'+invite_id
            #---------------------------------------------------------------------------------------------------------------------------email-
        if error_log:
            return Response(error_log)
        return Response('invitations were sent successfully' ,status=status.HTTP_200_OK)