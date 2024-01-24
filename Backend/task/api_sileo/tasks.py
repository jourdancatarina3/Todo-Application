from sileo.sileo.resource import Resource
from sileo.sileo.registration import register

from task.models import Task, CustomList
from task.forms import TaskForm, CustomListForm

class TaskResource(Resource):
    query_set = Task.objects.exclude(removed=True)

    allowed_methods = [
        'filter', 'get_pk', 'create', 'update', 'delete'
    ]

    fields = [
        'pk', 'title', 'description', 'status', 'due_date'
    ]

    update_filter_fields = ['pk']
    delete_filter_fields = ['pk']

    size_per_request = 50

    form_class = TaskForm

class CustomListResource(Resource):
    query_set = CustomList.objects.all()

    allowed_methods = [
        'filter', 'get_pk', 'create', 'update', 'delete'
    ]

    fields = [
        'pk', 'custom_list'
    ]

    update_filter_fields = ['pk']
    delete_filter_fields = ['pk']

    size_per_request = 1

    form_class = CustomListForm


register('task', 'tasks', TaskResource, version='v1')
register('custom', 'custom-list', CustomListResource, version='v1')
