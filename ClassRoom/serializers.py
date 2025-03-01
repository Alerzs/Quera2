from rest_framework import serializers
from .models import Classes ,ClassRoles ,Assignment ,Question ,Team ,Scores


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoles
        fields = ['user', 'role']

class ClassSerializer(serializers.ModelSerializer):
    owner_users = serializers.SerializerMethodField()
    teacher_users = serializers.SerializerMethodField()
    mentor_users = serializers.SerializerMethodField()
    student_users = serializers.SerializerMethodField()

    def validate(self, data):
        instance = self.instance

        if instance:
            current_attendent = instance.attendent()
            if 'capacity' in data and data['capacity'] is not None:
                if current_attendent > data['capacity']:
                    raise serializers.ValidationError(f"Capacity cannot be less than the current attendance ({current_attendent}).")
        return data
    

class AssignmentSerializer(serializers.ModelSerializer):
    
    for_class = serializers.StringRelatedField()
    
    class Meta:
        model = Assignment
        exclude = ["id"]


class QuestionSerializer(serializers.ModelSerializer):

    soal = serializers.StringRelatedField()
    class Meta:
        model = Question
        exclude = ['id']


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scores
        exclude = ['id']








class ClassViewSer(serializers.ModelSerializer):
    
    class Meta:
        model = Classes
        fields = '__all__'

class ClassDetailSer(serializers.ModelSerializer):
    
    class Meta:
        model = Classes
        fields = ['shenase', 'name', 'description', 'permision', 'password']
        lookup_field = 'shenase'


class JoinClassSer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoles
        fields = ['id', 'kelas', 'user', 'role']
        read_only_fields = ['id', 'kelas', 'user', 'role']

    
        def validate(self, data):
            class_instance = self.context['class_instance']  
            
            if class_instance.permision == 'pri':
                provided_password = data.get('password')
                if not provided_password or provided_password != class_instance.password:
                    raise serializers.ValidationError({"password": "Incorrect class password."})

            data.pop('password', None) 
            return data

