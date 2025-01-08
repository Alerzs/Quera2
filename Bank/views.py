from .models import *
from Bank.models import *
from Authentication.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , IsAdminUser ,AllowAny
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import json
from django.shortcuts import get_object_or_404
import requests
from .serializers import *


class SoalView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        if self.request.method == 'GET':
            return [AllowAny()]
    
    def post(self ,request):
        serializer = SoalSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self ,request):
        soals = Soal.objects.all()
        serializer = SoalSerializer(soals,many=True)
        return Response(serializer.data ,status=status.HTTP_200_OK)   
    

# class SoalDetails(APIView):--------------------------------------------------------------------
class Solve(APIView):
    permission_classes = [IsAuthenticated]
    def post(self ,request):
        my_user = request.user
        soal_id = request.data.get("soal_id")
        code = request.data.get("code")
        language = request.data.get("language")
        version = request.data.get("version")
        my_soal = get_object_or_404(Soal ,id =soal_id)
        if my_soal.answer_type != 'C':
            return Response("code is not allowed for text andfile ansering types")
        
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
        return Response(my_submit.mark)


class SolveFile(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    def post(self ,request):
        my_user = request.user
        soal_id = request.data.get("soal_id")
        file = request.data.get('file')
        my_soal = get_object_or_404(Soal ,id=soal_id)
        if my_soal.answer_type != 'F':
            return Response("code is not allowed for text andfile ansering types")
        if file:
            SubmitedAnswer.objects.create(user=my_user,soal=my_soal,submited_file=file)
            return Response("your answer is submited",status=status.HTTP_201_CREATED)
        return Response("file is missing",status=status.HTTP_400_BAD_REQUEST)