from .models import *
from rest_framework import generics
import random
from django.db import transaction
import requests
import json
from .permisions import IsClassOwner
from Bank.models import Soal
from Bank.models import *
from Authentication.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from .serializers import *
from Bank.serializers import SubmitionSerializer
from Bank.serializers import SoalSerializer


class Classview(generics.ListCreateAPIView):
    queryset = Classes.objects.all()
    serializer_class = ClassViewSer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(classroles__user=self.request.user)
    
    def perform_create(self, serializer):
        if serializer.is_valid():
            with transaction.atomic():
                my_user = self.request.user
                name = serializer.validated_data['name']

                my_forum = Forum.objects.create(name=f"{name} forum")
                my_forum.participents.add(my_user)

                my_class = serializer.save(shenase=get_random_string(20),forum=my_forum)
            
                ClassRoles.objects.create(user=my_user, kelas=my_class, role='O')
            return Response({'detail': 'Class created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClassDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'shenase'
    serializer_class = ClassDetailSer
    queryset = Classes.objects.all()
    permission_classes = [IsAuthenticated,IsClassOwner]

        
class JoinClass(generics.CreateAPIView):
    serializer_class = JoinClassSer
    queryset = ClassRoles.objects.all()
    permission_classes = [IsAuthenticated]       

    def create(self, request, shenase, *args, **kwargs):

        class_instance = get_object_or_404(Classes, shenase=shenase)
        serializer = self.get_serializer(data=request.data, context={'class_instance': class_instance})
        if serializer.is_valid():
            if ClassRoles.objects.filter(kelas=class_instance, user=self.request.user).exists():
                raise serializers.ValidationError({"error": "User is already a member of this class."})
            serializer.save(kelas=class_instance, user=self.request.user, role='S')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JoinClassByInvitation(generics.RetrieveAPIView):
    queryset = Invite.objects.all()
    serializer_class = InviteSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'invite_id'

    def retrieve(self, request, *args, **kwargs):
        invite = self.get_object()
        
        if request.user != invite.reciver:
            return Response({'error': 'You are not authorized to accept this invite.'}, status=403)
        class_role, created = ClassRoles.objects.get_or_create(user=request.user,kelas=invite.target_class,defaults={'role': 'S'})
        if created:
            invite.delete()
            return Response({'message': 'You have successfully joined the class.'})
        else:
            return Response({'message': 'You are already a member of this class.'})


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
    
class InClassMessage(APIView):
    permission_classes = [IsAuthenticated]
    def post(self ,request ,shenase):
        my_user = request.user
        text = request.data.get('text')
        my_class = get_object_or_404(Classes ,shenase=shenase)
        my_forum = my_class.forum
        if my_forum.participents.filter(id=my_user.id).exists():
            Message.objects.create(sender=my_user,room=my_forum,text=text)
            return Response('your message was sent',status=status.HTTP_200_OK)
        return Response('you dont have access to the selected chatroom' ,status=status.HTTP_403_FORBIDDEN)
    

class ChatBox(APIView):
    permission_classes = [IsAuthenticated]
    def get(self ,request ,shenase):
        my_user = request.user
        my_class = get_object_or_404(Classes ,shenase=shenase)
        my_forum = my_class.forum
        if my_forum.participents.filter(id=my_user.id).exists():
            return Response(Message.objects.filter(room=my_forum).order_by("send_time").values_list("sender__username","text","send_time") ,status=status.HTTP_200_OK)
        return Response('you dont have access to the selected chatroom' ,status=status.HTTP_403_FORBIDDEN)


class AssignmentView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self ,request ,shenase):
        name = request.data.get("name")
        contribution_type = request.data.get("contribution_type")
        marking_type = request.data.get("marking_type")
        if not name or not contribution_type or not marking_type:
            return Response("name , contribution_type and marking_type are required ")
        my_user = request.user
        my_class = get_object_or_404(Classes ,shenase=shenase)
        try:
            if ClassRoles.objects.get(user=my_user, kelas=my_class).role == 'S':
                return Response("students dont have permission to add assignment",status=status.HTTP_403_FORBIDDEN)
        except:
            return Response("no permissions" ,status=status.HTTP_403_FORBIDDEN)
        
        Assignment.objects.create(name=name,contribution_type=contribution_type,marking_type=marking_type,for_class=my_class)
        return Response("assignment added",status=status.HTTP_201_CREATED)
        
    def get(self ,request ,shenase):
        my_user = request.user
        my_class = get_object_or_404(Classes ,shenase=shenase)
        try:
            ClassRoles.objects.get(user=my_user, kelas=my_class)
        except:
            return Response("no permissions" ,status=status.HTTP_403_FORBIDDEN)
        
        assignemnts = Assignment.objects.filter(for_class=my_class)
        serializer = AssignmentSerializer(assignemnts ,many=True)
        return Response(serializer.data ,status=status.HTTP_200_OK)
    

class AddGroup(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self ,request ,shenase):
        group_list = request.data.get('group_list',[])
        assignment_id = request.data.get('assignment_id')
        number_of_random_groups = request.data.get('number_of_random_groups')

        my_assignment = get_object_or_404(Assignment, id=assignment_id)
        my_user = request.user
        my_class = get_object_or_404(Classes ,shenase=shenase)

        if my_assignment.contribution_type == "I":
            return Response("creating groups is not allowed in individual contribution type", status=status.HTTP_400_BAD_REQUEST)
        if len(group_list) > 10:
            return Response('maximum number of groups is 10' ,status=status.HTTP_400_BAD_REQUEST)
        if my_assignment.for_class != my_class:
            return Response("no permission", status=status.HTTP_403_FORBIDDEN)
        try:
            if ClassRoles.objects.get(user=my_user ,kelas=my_class).role == 'S':
                return Response("students dont have permission to add group",status=status.HTTP_403_FORBIDDEN)
        except:
            return Response("no permission", status=status.HTTP_403_FORBIDDEN)
        
        if number_of_random_groups:
            attendence = ClassRoles.objects.filter(kelas=my_class,role='S')
            if len(attendence) < 2 * number_of_random_groups:
                return Response("each grop must have at least 2 members", status=status.HTTP_400_BAD_REQUEST)
            for _ in range(number_of_random_groups):
                std = random.sample(list(attendence),k=len(attendence)//number_of_random_groups)
                my_team = Team.objects.create()
                for item in std:
                    my_team.members.add(item.user)
                    attendence = attendence.exclude(id=item.pk)
                my_assignment.teams.set(my_team)
                number_of_random_groups -= 1
            return Response("group was created" ,status=status.HTTP_201_CREATED)
        
        combined_lists = [item for lst in group_list for item in lst]
        seen = set()
        duplicates = set()
        try:
            for value in combined_lists:
                if not ClassRoles.objects.filter(user=QueraUser.objects.get(id=value),kelas=my_class,role='S').exists():
                    return Response(f"user {value} is not student of {my_class.name}")
                if value in seen:
                    duplicates.add(value)
                else:
                    seen.add(value)
            if duplicates:
                return Response({"Duplicate values found.": list(duplicates)})
        except:
            return Response(f"no user found with {value} value", status=status.HTTP_400_BAD_REQUEST)

        my_assignment.teams.clear()
        for team in group_list:
            my_team = Team.objects.create()
            students = QueraUser.objects.filter(id__in=team)
            my_assignment.teams.add(my_team.members.add(*students))
            my_assignment.save()
            my_team.save()
        return Response("group was created" ,status=status.HTTP_201_CREATED)
    


class AddQuestionFromBank(APIView):
    permission_classes = [IsAuthenticated]
    def post(self ,request ,shenase):
        assignment_id = request.data.get('assignment_id')
        question_id = request.data.get('question_id')
        deadline = request.data.get('deadline')
        send_limit = request.data.get('send_limit')
        mark = request.data.get('mark')
        late_penalty = request.data.get('late_penalty')

        if not assignment_id or not question_id or not deadline or not send_limit or not mark or not late_penalty:
            return Response("assignment_id , question_id , deadline , send_limit , mark and late_penalty are required")
        my_assignment = get_object_or_404(Assignment, id=assignment_id)
        my_soal =  get_object_or_404(Soal, id=question_id)
        my_user = request.user
        my_class = get_object_or_404(Classes ,shenase=shenase)

        if my_assignment.for_class != my_class:
            return Response("no permission", status=status.HTTP_403_FORBIDDEN)
        try:
            if ClassRoles.objects.get(user=my_user ,kelas=my_class).role == 'S':
                return Response("students dont have permission to add group",status=status.HTTP_403_FORBIDDEN)
        except:
            return Response("no permission", status=status.HTTP_403_FORBIDDEN)
        
        my_question = my_assignment.questions.create(soal=my_soal,deadline=deadline,send_limit=send_limit,mark=mark,late_penalty=late_penalty)
        serializer = QuestionSerializer(my_question)
        return Response(serializer.data ,status=status.HTTP_201_CREATED)
    

class AddCreatedQuestion(APIView):
    permission_classes = [IsAuthenticated]
    def post(self ,request ,shenase):
        assignment_id = request.data.get('assignment_id')
        deadline = request.data.get('deadline')
        send_limit = request.data.get('send_limit')
        mark = request.data.get('mark')
        late_penalty = request.data.get('late_penalty')

        if not assignment_id or not deadline or not send_limit or not mark or not late_penalty:
            return Response("assignment_id , deadline , send_limit , mark and late_penalty are required")
        my_assignment = get_object_or_404(Assignment, id=assignment_id)
         
        my_user = request.user
        my_class = get_object_or_404(Classes ,shenase=shenase)
        serializer = SoalSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save() 
            my_soal = serializer.instance
            if my_assignment.for_class != my_class:
                return Response("no permission", status=status.HTTP_403_FORBIDDEN)
            try:
                if ClassRoles.objects.get(user=my_user ,kelas=my_class).role == 'S':
                    return Response("students dont have permission to add group",status=status.HTTP_403_FORBIDDEN)
            except:
                return Response("no permission", status=status.HTTP_403_FORBIDDEN)
            
            my_question = my_assignment.questions.create(soal=my_soal,deadline=deadline,send_limit=send_limit,mark=mark,late_penalty=late_penalty)
            serializer = QuestionSerializer(my_question)
            return Response(serializer.data ,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self ,request ,shenase ,assignment_id ,question_id):
        
        my_assignment = get_object_or_404(Assignment ,id = assignment_id)
        my_user = request.user
        my_class = get_object_or_404(Classes ,shenase=shenase)
        my_question = Question.objects.filter(assignment=my_assignment)
        if my_assignment.for_class != my_class:
            return Response("assignment is not for class", status=status.HTTP_403_FORBIDDEN)
        if not ClassRoles.objects.filter(user=my_user,kelas=my_class).exists():
            return Response("user is not part of the class" ,status=status.HTTP_403_FORBIDDEN)
        serializer = QuestionSerializer(my_question ,many=True)
        return Response(serializer.data ,status=status.HTTP_200_OK)
    
    def post(self ,request ,shenase ,assignment_id ,question_id):

        my_user = request.user
        my_class = get_object_or_404(Classes ,shenase=shenase)
        my_assignment = get_object_or_404(Assignment ,id=assignment_id)
        my_question = get_object_or_404(Question ,id =question_id)
        my_soal = my_question.soal
        if my_question not in my_assignment.questions.all():
            return Response("question not for assignment")
        if my_assignment.for_class != my_class:
            return Response("assignmnet not for class")
        if not ClassRoles.objects.filter(user=my_user,kelas=my_class).exists():
            return Response("user is not member of the class")
        if my_question.soal.answer_type == 'F': 
            file = request.data.get('file')
            if file:
                SubmitedAnswer.objects.create(user=my_user,soal=my_soal,submited_file=file)
                Scores.objects.create(student=my_user,question=my_question)
                return Response("your answer is submited",status=status.HTTP_201_CREATED)
            return Response("file is missing",status=status.HTTP_400_BAD_REQUEST)
        if my_question.soal.answer_type == 'C':
            code = request.data.get("code")
            language = request.data.get("language")
            version = request.data.get("version")
            my_submit = SubmitedAnswer.objects.create(user=my_user,soal=my_soal,submited_code=code)
            result = ""
            solution = my_soal.test_case_answer.split(',')
            correct_count = 0
            for index , test in enumerate(my_soal.test_case.split(',')):
                my_data = {
                    "clientId":"a7635a08ebc4743dc3e11dc40c2665c9",
                    "clientSecret":"9306508b9b470f9a53d50f8465688bd2622da9d98053b260093ed27106e5f409",
                    "script":code,
                    "stdin":test,
                    "language":language,
                    "versionIndex":version
                }
                res = json.loads(requests.post("https://api.jdoodle.com/v1/execute",json=my_data).content.decode('utf-8'))
                if solution[index] == res["output"]:
                    correct_count += 1
                if res["isExecutionSuccess"]:
                    result = result + res["output"] + ","
                else:
                    result = "error,"
            my_submit.result = result
            try:
                my_submit.mark = len(solution) // correct_count
            except:
                my_submit.mark = 0
            my_submit.save()
            if my_assignment.marking_type == 'J':
                my_score = Scores.objects.create(student=my_user,question=my_question,taken_mark=my_submit.mark*my_question.mark)
                return Response(my_score.taken_mark ,status=status.HTTP_200_OK)
            my_score = Scores.objects.create(user=my_user,question=my_question)
            return Response("answer was submited",status=status.HTTP_200_OK)
        if my_question.soal.answer_type == 'F':
            file = request.data.get('file')
            if file:
                SubmitedAnswer.objects.create(user=my_user,soal=my_soal,submited_file=file)
                my_score = Scores.objects.create(user=my_user,question=my_question)
                return Response("your answer is submited",status=status.HTTP_201_CREATED)
            return Response("file is missing",status=status.HTTP_400_BAD_REQUEST)

class GiveMark(APIView):
    permission_classes = [IsAuthenticated]

    def get(self ,request ,shenase ,assignment_id):
        my_user = request.user
        my_class = get_object_or_404(Classes ,shenase=shenase)
        my_assignment = get_object_or_404(Assignment ,id=assignment_id)
        if my_assignment.for_class != my_class:
            return Response("assignmnet not for class")
        if not ClassRoles.objects.filter(user=my_user,kelas=my_class).exclude(role='S').exists():
            return Response("yo dont have permision to see submitions")
        my_students = QueraUser.objects.filter(classroles__kelas=my_class,classroles__role='S')
        my_soal = Soal.objects.filter(question__assignment=my_assignment)
        all_submitions = SubmitedAnswer.objects.filter(user__in=my_students,soal__in=my_soal)
        for item in all_submitions:
            if not Scores.objects.filter(student=item.user ,question__soal=item.soal).exists():
                all_submitions.exclude(item)
        serializer = SubmitionSerializer(all_submitions,many=True)
        return Response(serializer.data ,status=status.HTTP_200_OK)
    
    def post(self ,request ,shenase ,assignment_id):
        mark = request.data.get('mark')
        student_username = request.data.get('student_username')
        question_name = request.data.get('question_name')
        my_user = request.user
        my_class = get_object_or_404(Classes ,shenase=shenase)
        my_assignment = get_object_or_404(Assignment ,id=assignment_id)
        if my_assignment.marking_type == 'J':
            return Response("this assignment is marked by judge")
        if my_assignment.for_class != my_class:
            return Response("assignmnet not for class")
        if not ClassRoles.objects.filter(user=my_user,kelas=my_class).exclude(role='S').exists():
            return Response("yo dont have permision to give marks")
        my_student = get_object_or_404(QueraUser ,username=student_username)
        my_question = get_object_or_404(Question ,soal__name=question_name)
        my_score = Scores.objects.get(question=my_question,student=my_student)
        my_score.taken_mark = mark
        my_score.save()
        serializer = ScoreSerializer(my_score)
        return Response(serializer.data)
    

class ScoreBoard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self ,request ,shenase ,assignment_id):
        my_user = request.user
        my_class = get_object_or_404(Classes ,shenase=shenase)
        my_assignment = get_object_or_404(Assignment ,id=assignment_id)
        my_questions = Question.objects.filter(assignment=my_assignment)
        my_students = QueraUser.objects.filter(classroles__role='S',classroles__kelas=my_class)
        all_scores = Scores.objects.filter(student__in=my_students ,question__in=my_questions)
        serializer = ScoreSerializer(all_scores)
        print(all_scores)
        return Response(serializer.data)