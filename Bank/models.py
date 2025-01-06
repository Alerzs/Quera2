from django.db import models
from Authentication.models import QueraUser
from django.core.validators import MinValueValidator , MaxValueValidator

class Soal(models.Model):

    ANSWER_CHOICE = [
        ('F','file'),
        ('C','code'),
        ('T','text')
    ]
    LEVEL_CHOICE =[
        ('E','easy'),
        ('M','medium'),
        ('H','hard')
    ]

    name = models.CharField(max_length=25)
    creator = models.ForeignKey(QueraUser ,on_delete=models.CASCADE)
    category =models.CharField(max_length=20)
    level = models.CharField(max_length=1 ,choices=LEVEL_CHOICE)
    soorat = models.TextField()
    answer_type = models.CharField(max_length=1, choices=ANSWER_CHOICE ,default="C")
    test_case = models.TextField(blank=True ,null=True)
    test_case_answer = models.TextField(blank=True ,null=True)



class SubmitedAnswer(models.Model):
    user = models.ForeignKey(QueraUser ,on_delete=models.CASCADE)
    soal = models.ForeignKey(Soal ,on_delete=models.CASCADE)
    submited_file = models.FileField(blank=True ,null=True ,upload_to='uploads/')
    submited_code = models.TextField(blank=True ,null=True)
    result = models.TextField(editable=False ,blank=True ,null=True)
    mark = models.PositiveIntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)],editable=False ,blank=True ,null=True)
    
