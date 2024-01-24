from django.contrib import admin
from .models import Task, CustomList

class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "description", "status", "due_date"]

admin.site.register(Task, TaskAdmin)

class CustomListAdmin(admin.ModelAdmin):
    list_display = ["custom_list"]

admin.site.register(CustomList, CustomListAdmin)