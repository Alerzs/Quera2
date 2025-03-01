from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from Authentication.models import QueraUser
from Bank.models import Soal
from django.db.models import Count ,Q
from rest_framework.exceptions import ValidationError


class Forum(models.Model):
    name = models.CharField(max_length=25)
    participents = models.ManyToManyField(QueraUser)

    def __str__(self) -> str:
        return self.name


class Message(models.Model):
    sender = models.ForeignKey(QueraUser ,on_delete=models.CASCADE)
    room = models.ForeignKey(Forum ,on_delete=models.CASCADE)
    text = models.TextField()
    send_time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.text


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
    forum = models.OneToOneField(Forum ,on_delete=models.CASCADE ,blank=True ,null=True)

    def __str__(self) -> str:
        return self.name

    def is_owner(self ,user):
        return ClassRoles.objects.filter(user=user ,role='O').exists()

    def attendent(self):
        return ClassRoles.objects.filter(kelas=self).aggregate(attend=Count("user",filter=Q(role='S')))["attend"]

    def clean(self) -> None:
        if self.permision == 'pub' and self.password:
            raise ValidationError('password must be blank when the class permision is public')
        
        if self.permision == 'per' and not self.password:
            raise ValidationError('classes with  privet permision must have a password')
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    

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

    soal = models.ForeignKey(Soal ,on_delete=models.CASCADE)#---------------az soal
    deadline = models.DateTimeField()
    send_limit = models.PositiveSmallIntegerField()
    mark = models.PositiveSmallIntegerField()
    late_penalty = models.PositiveSmallIntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)])

    def __str__(self) -> str:
        return self.soal.name


class Scores(models.Model):
    question =models.ForeignKey(Question ,on_delete=models.CASCADE)
    student = models.ForeignKey(QueraUser ,on_delete=models.CASCADE)
    taken_mark = models.PositiveSmallIntegerField()


class Team(models.Model):
    members = models.ManyToManyField(QueraUser)

    def __str__(self) -> str:
        return ", ".join(member.username for member in self.members.all())


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
    
    def __str__(self) -> str:
        return self.name
    
    def clean(self) -> None:
        if self.contribution_type == 'I' and self.teams.exists():
            raise ValidationError('teams are not allowed in individual contribution type')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Invite(models.Model):
    
    target_class = models.ForeignKey(Classes ,on_delete=models.CASCADE)
    reciver = models.ForeignKey(QueraUser ,on_delete=models.CASCADE)
    invite_id = models.CharField(max_length=20 ,unique=True ,editable=False)

