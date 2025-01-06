from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from Authentication.models import QueraUser
from Bank.models import Soal



class Forum(models.Model):
    name = models.CharField(max_length=25)
    participents = models.ManyToManyField(QueraUser)


class Message(models.Model):
    sender = models.ForeignKey(QueraUser ,on_delete=models.CASCADE)
    room = models.ForeignKey(Forum ,on_delete=models.CASCADE)
    text = models.TextField()
    send_time = models.DateTimeField(auto_now_add=True)


class Classes(models.Model):

    PERMISION_CHOICE = [
        ('pri','private'),
        ('pub','public')
    ]

    name = models.CharField(max_length=20)
    description = models.TextField(blank=True , null=True)
    shenase = models.CharField(max_length=20 ,unique=True ,editable=False)
    capacity = models.PositiveIntegerField(blank=True , null=True)
    
    permision = models.CharField(max_length=3 ,choices=PERMISION_CHOICE)
    password = models.CharField(max_length=20, default=None , blank=True ,null=True)
    join_time = models.DateTimeField(blank=True , null=True)

    forum = models.OneToOneField(Forum ,on_delete=models.CASCADE)
    

class ClassRoles(models.Model):

    ROLE_CHOICE =[
        ('O','owner'),
        ('T','Teacher'),
        ('M','mentor'),
        ('S','student')
    ]
    user = models.ForeignKey(QueraUser ,on_delete=models.CASCADE)
    kelas = models.ForeignKey(Classes ,on_delete=models.CASCADE)
    role = models.CharField(max_length=1,choices=ROLE_CHOICE)


class Question(models.Model):

    soal = models.ForeignKey(Soal ,on_delete=models.CASCADE)
    deadline = models.DateTimeField()
    send_limit = models.PositiveSmallIntegerField()
    mark = models.PositiveSmallIntegerField()
    late_penalty = models.PositiveSmallIntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)])


class Scores(models.Model):
    question =models.ForeignKey(Question ,on_delete=models.CASCADE)
    student = models.ForeignKey(QueraUser ,on_delete=models.CASCADE)
    taken_mark = models.PositiveSmallIntegerField()


class Team(models.Model):
    members = models.ManyToManyField(QueraUser)


class Assignment(models.Model):

    CONTRIB_CHOICE =[
        ('I','individual'),
        ('G','group')
    ]
    MARKING_CHOICE =[
        ('T','teacher'),
        ('J','judge')
    ]

    name = models.CharField(max_length=25)
    contribution_type = models.CharField(max_length=1 ,choices=CONTRIB_CHOICE)
    marking_type = models.CharField(max_length=1 ,choices=MARKING_CHOICE)
    teams = models.ManyToManyField(Team)
    questions = models.ManyToManyField(Question)
    for_class = models.ForeignKey(Classes ,on_delete=models.CASCADE)
