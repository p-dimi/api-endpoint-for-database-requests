from rest_framework import serializers
from .models import ClicksInfo

class ClicksInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClicksInfo
        fields = '__all__'