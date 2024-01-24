from rest_framework import serializers

from .models import Task
from .models import CustomList

class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'due_date')

class CustomListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomList
        fields = ['id', 'custom_list']