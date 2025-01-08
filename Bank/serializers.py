from rest_framework import serializers
from .models import *


class SoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Soal
        fields = ['name', 'category', 'level', 'soorat', 'answer_type', 'test_case', 'test_case_answer']
        read_only_fields = ['creator']

    def validate(self, data):
        answer_type = data.get('answer_type')
        test_case = data.get('test_case')
        test_case_answer = data.get('test_case_answer')
    
        if answer_type != 'C' and (test_case or test_case_answer):
            raise serializers.ValidationError("Questions with file or text answering type should not have test case")
        if answer_type == 'C' and (not test_case or not test_case_answer):
            raise serializers.ValidationError("Questions with code answering type should have test case")
        return data

    def create(self, validated_data):

        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)
    

class SubmitionSerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField()
    soal = serializers.StringRelatedField()
    class Meta:
        model = SubmitedAnswer
        fields = ['id','user','soal','submited_code']

