from rest_framework import serializers
from .models import *

class QUSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueraUser
        fields = ['username', 'name', 'password', 'phone']