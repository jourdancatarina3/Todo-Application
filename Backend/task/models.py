from django.db import models

class Task(models.Model):

    title = models.CharField(max_length=155, default='')
    description = models.CharField(max_length=510)
    status = models.CharField(max_length=10)
    removed = models.BooleanField(default=False)
    due_date = models.CharField(max_length=55, null=True, blank=True)

class CustomList(models.Model):
    custom_list = models.CharField(max_length=200, null=True, blank=True, default='')