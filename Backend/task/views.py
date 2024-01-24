from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Task, CustomList
from .serializers import TaskSerializer, CustomListSerializer

from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

class TaskViewSet(viewsets.ModelViewSet):
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class CustomListViewSet(viewsets.ModelViewSet):
    queryset = CustomList.objects.all()
    serializer_class = CustomListSerializer

    def list(self, request, *args, **kwargs):
        instance = self.queryset.first()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)