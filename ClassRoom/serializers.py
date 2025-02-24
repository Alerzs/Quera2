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