from django import forms

from task.models import Task, CustomList

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'status', 'due_date'
        ]
class CustomListForm(forms.ModelForm):
    class Meta:
        model = CustomList
        fields = [
            'custom_list'
        ]