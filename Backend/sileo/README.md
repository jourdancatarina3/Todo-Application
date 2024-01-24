# SILEO

A REST framework for channelfix.


### `sileo.resource.Resource`

The `Resource` class is the base class and the core of sileo. A subclass of `Resource` can be used
to serialize a model instance or as a REST api endpoint.

Given the model:

``` python
from django.db import models


class Foo(models.Model):
    bar = models.CharField(max_length=100)
```

A resource for the Foo model can look like
``` python
from sileo.resource import Resource
from sile.registration import register

from models import Foo


class FooResource(Resource):

    query_set = Foo.objects.all()
    fields = ['bar']
    allowed_methods = ['get_pk', 'filter']
    filter_fields = ('bar__icontains',)

    is_cached = True
    cache_timeout = 120
    cache_prefix = 'foo'


# if you want to make your resource accessible via HTTP request
register(namespace='foo-space', name='foo', resource=FooResource)

```

`query_set` is the base query used in the `get_pk` and `filter` method

`fields` is a list of field names or properties that are included in the serialized result


`allowed_methods` is a list of methods (`get_pk`, `filter`, `form_dict`, `create`, `update`, `delete`) that the Resource supports

`filter_fields` is a list of optional filter parameters that the user can specify. For example, with the resource defined above
when you access the filter the resulting query_set can be `Foo.objects.all().filter(bar__icontains='what ever was provided')`

`is_cached` is a boolean that is set to True if you want the resource's output/result to be cached. Note that the caching is per record/instance not per query.

`cache_timeout` is an integer indicating how long you want the cached in seconds

`cache_prefix` specifies the prefix for the cache key used. In the example about a cache key can be `foo_1` since the cache key
is a combination of the cache_prefix and the instance pk


### `sileo.fields`
The fields module contains a couple of classes that can be used allow your Resource to serialize fields or properties that are
not normally serializable.

##### `sileo.fields.ResourceModel`
`ResourceModel` is used to resolve fields/properties that returns a model instance
```python
from django.db import models
from django.contrib.auth.models import User


class Foo(models.Model):
    owner = models.Foreignkey(User, related_name='foos')
    bar = models.CharField(max_length=100)
```
```python
from django.contrib.auth.models import User

from models import Foo

from sileo.resource import Resource
from sileo.fields import ResourceModel


class UserResource(Resource):
    query_set = User.objects.all()
    fields = ['pk', 'username']


class FooResource(Resource):
    query_set = Foo.objects.all()
    fields = ['bar', ResourceModel('owner', resource=UserResource)]
    # if your resolver class is registered you can use the name and names to specify it
    # fields = [ResourceModel('owner', 'namespace', 'name')]
```
This results to:
```json
{
    "bar": "sample",
    "owner": {
        "pk": 1,
        "username": "user1"
    }
}
```

##### `sileo.fields.ResourceModelManager`
`ResourceModelManager` is used to resolve fields/properties that returns a model manager

##### `sileo.fields.ResourceQuerySet`
`ResourceQuerySet` is used to resolve properties that returns a queryset

##### `sileo.fields.ResourceGenericModel`
`ResourceGenericModel` is used to resolve fields/properties that returns instances of different types, this is especially useful for GenericForeignkeys

```python
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Bar(models.Model):
    target_type = models.ForeignKey(ContentType)
    target_id = models.PositiveIntegerField()
    target = GenericForeignKey('target_type', 'target_id')
    foo = models.CharField(max_length=100)
```
```python
from django.contrib.auth.models import User

from models import Bar

from sileo.resource import Resource
from sileo.fields import ResourceGenericModel


class UserResource(Resource):
    query_set = User.objects.all()
    fields = ['pk', 'username']


class BarResource(Resource):
    query_set = Bar.objects.all()
    fields = ['foo', ResourceGenericModel('target', {'User': UserResource})]
    # if your resolver class is registered you can use the name and names to specify it
    # fields = ['foo', ResourceGenericModel('target', {'User': ('namespace', 'name')})]
```

##### `sileo.fields.ResourceTypeConvert`
`ResourceTypeConvert` allows you to provide a function that converts the field/property to something that is serializable
```python
from django.db import models


class Bar(models.Model):
    foo = models.DecimalField(max_digits=12, decimal_places=5)
```
```python
from models import Bar

from sileo.resource import Resource
from sileo.fields import ResourceTypeConvert


class FooResource(Resource):
    query_set = Bar.objects.all()
    # covert decimal field to string
    fields = [ResourceTypeConvert('foo', str)]
```

##### `sileo.fields.ResourceMethodField`
`ResourceMethodField` is for creating custom fields within your Resource via method.
```python
class UserResource(Resource):

    query_set = User.objects.all()

    fields = (
        'first_name', 'last_name',
        ResourceMethodField(
            'full_name', method_name='get_full_name_field')
    )

    def get_full_name_field(self, prop, obj, request):
        return '%s %s' % (obj.first_name, obj.last_name)
```

`@NOTE!!!!`
it is prefereable to use the prefix `get` and suffix `field` for naming conventions
to avoid conflicts with parent methods.

## Resource Methods

The `Resource` class has the following methods that allows you to preform
`get`, `filter`, `form_dict`, `create`, `update`, and `delete` via HTTP request.

#####  `get_pk`
The `get_pk` method allows you to get data about an instance given its `pk`.

```python
class FooResource(Resource):

    query_set = Foo.objects.all()
    fields = ['title']
    allowed_methods = ['get_pk']


register(namespace='foo-space', name='foo', resource=FooResource)
```
The resource above allows you to get the `title` of a Foo instance given its `pk` using the `get_pk` method. Note that
you have to indicate that the resource allows the `get_pk` method by adding it in the `allowed_methods` list.

Now in your javascript code you can access the get_pk method of this resource using the sileo js library.
```javascript
var Foo = new sileo.Model('foo-space', 'foo');

Foo.objects.get(1).then(function(data) {
    console.log(data);
}).catch(function(xhr) {
    console.log('Foo with pk=1 does not exists');
});
```
Given the js code above, assuming that a Foo with pk=1 exists in your database and its title is "my foo", you will
get this result in your console:
```json
{
    "title": "my foo"
}
```

##### `filter`
The `filter` method allows you to get a list containing the data of the instances that matches your filters.

```python
class FooResource(Resource):

    query_set = Foo.objects.all()
    fields = ['title']
    allowed_methods = ['filter']
    filter_fields = ['title__icontains']


register(namespace='foo-space', name='foo', resource=FooResource)
```
The resource above allows you to get Foo instances that has a title containing a given string.

In your javascript you can do something like
```javascript
var Foo = new sileo.Model('foo-space', 'foo');

Foo.objects.filter({'title__icontains': 'sample'}).then(function(data) {
    console.log(data);
})
```
And as a result you can get something like:
```json
[
    {
        "title": "sample foo"
    },
    {
        "title": "foo sample"
    }
]
```
If you want your filters to be required, you can add them in the `required_filter_fields` list instead of the `filter_fields` list.

Note that by default sileo only gives 7 results at a time. This is set by the `size_per_request` property of the `Resource` class, which you
can override.

If you want to get the next 7 you can do something like:
```javascript
Foo.objects.filter({'title__icontains': 'sample'}, {'top': 7}).then(function(data) {
    console.log(data);
})
```
The `top` key indicates the offset from the top of the list.

##### `form_dict`
The `form_dict` method allows you go get the information you normally get when you have a django form instance in a json format.
This method is normally used for rendering forms using javascript with code that looks like django.

Let's say you have a model like
```python
from django.db import models


class Foo(models.Model):
    title = models.CharField(max_length=50)
```
To have an api Resource with a working `form_dict` method you need to specify the `form_class` property of your Resource
```python
from forms import FooForm


class FooResource(Resource):
    query_set = Foo.objects.all()
    fields = ['title']
    allowed_methods = ['form_dict']
    form_class = FooForm


register(namespace='foo-space', name='foo', resource=FooResource)
```
and the form class should be a subclass for sileo's own form class that inherits from django's form class but adds extra methods. e.g.
```python
from sileo.forms import ModelForm
from models import Foo


class FooForm(ModelForm):
    class Meta:
        model = Foo
        fields = ('title',)
```
Now in your javascript you can do something like
```javascript
var Foo = new sileo.Model('foo-space', 'foo');

Foo.objects.form_dict().then(function(data) {
    console.log(data);
}).catch(function(xhr) {
    console.log('Something went wrong!');
});
```
And get the result
```json
{
    "title": "FooForm",
    "prefix": null,
    "data": {
        "title": null
    },
    "fields": {
        "title": {
            "auto_id": "id_title",
            "help_text": "",
            "html_name": "title",
            "label": "Title",
            "name": "title",
            "required": true,
            "value": null
        }
    }
}
```
You can also specify the a set of filters to get the instance that you want to populate your form. This is helpful when you want to edit an instance. You will have
to set the `update_filter_fields` property of your Resource to get this going. Something like:
```python
from forms import FooForm


class FooResource(Resource):
    query_set = Foo.objects.all()
    fields = ['title']
    allowed_methods = ['form_dict']
    form_class = FooForm

    update_filter_fields = ('pk',) # specify a list of filter fields used as filters to get the instance for form_dict and update method


register(namespace='foo-space', name='foo', resource=FooResource)
```
Then in your javascript you can do
```javascript
Foo.objects.form_dict({'pk': 1}).then(function(data) {
    console.log(data);
}).catch(function(xhr) {
    console.log('Something went wrong!');
});
```
And get the result
```json
{
    "title": "FooForm",
    "prefix": null,
    "data": {
        "title": "my foo"
    },
    "fields": {
        "title": {
            "auto_id": "id_title",
            "help_text": "",
            "html_name": "title",
            "label": "Title",
            "name": "title",
            "required": true,
            "value": "my foo"
        }
    }
}
```

##### `create`
The `create` method allows you to create a new record using the `form_class` you specified. What the create method does is it will
pass the data from the request (POST and FILES) to the form instance and try to save the form.

Assuming we have the same form and model as above, our api resource can be like
```python
from forms import FooForm


class FooResource(Resource):
    query_set = Foo.objects.all()
    fields = ['title']
    allowed_methods = ['create']
    form_class = FooForm


register(namespace='foo-space', name='foo', resource=FooResource)
```
Your javascript can be like
```javascript
var Foo = new sileo.Model('foo-space', 'foo');

// Foo.objects.create(new FormData(form)).then(function(data) {  to pass a FormData instead of json
Foo.objects.create({'title': 'hello world'}).then(function(data) {
    console.log(data);
}).catch(function(xhr) {
    console.log('Something went wrong!');
});
```
If everything works well a new record will be added in the database, but if there are errors the `catch` callback gets
executed with the request object as the parameter. The form errors will be in the content of the request object.

##### `update`
The `update` method allows you to update an existing record using the `form_class` you specified. What the update method does is it will
get the instance given the values for the `update_filter_fields` and pass it along with the data from the request (POST and FILES) to the form instance and try to save the form.

Assuming we have the same form and model as above, our api resource can be like
```python
from forms import FooForm


class FooResource(Resource):
    query_set = Foo.objects.all()
    fields = ['title']
    allowed_methods = ['update']
    form_class = FooForm
    update_filter_fields = ('title',)


register(namespace='foo-space', name='foo', resource=FooResource)
```
Your javascript can be like
```javascript
var Foo = new sileo.Model('foo-space', 'foo');

// Foo.objects.update({'title': 'hello world'}, new FormData(form)).then(function(data) {  to pass a FormData instead of json
Foo.objects.update({'title': 'hello world'}, {'title': 'hello earth'}).then(function(data) {
    console.log(data);
}).catch(function(xhr) {
    console.log('Something went wrong!');
});
```
If everything works well the Foo instance with `title=hello world` will be updated and the new title will be 'hello earth', but if there are errors the `catch` callback gets
executed with the request object as the parameter. The form errors will be in the content of the request object.

It is important to note that all the filter fields listed in `update_filter_fields` are required, meaning if you have `title` on that list and in your javascript you did not
provide the title in the filters json it will result to a 404. Also the `update` method is meant to update only 1 record, meaning if the resulting query with your filters result
to more that 1 record it will 404.

##### `delete`
The `delete` method allows you to delete or just mark a record as removed given a filters defined in `delete_filter_fields`.

A resource that allows delete method looks like
```python
from forms import FooForm


class FooResource(Resource):
    query_set = Foo.objects.all()
    allowed_methods = ['delete']
    delete_filter_fields = ('pk',)


register(namespace='foo-space', name='foo', resource=FooResource)
```

and the javascript looks like
```javascript
var Foo = new sileo.Model('foo-space', 'foo');

Foo.objects.delete({'pk': 1}).then(function(data) {
    console.log(data);
}).catch(function(xhr) {
    console.log('Something went wrong!');
});
```
The snippet above will remove/delete the Foo with pk=1.

It is important to note that all the filter fields listed in `delete_filter_fields` are required, meaning if you have `pk` on that list and in your javascript you did not
provide the pk in the filters json it will result to a 404. Also the `delete` method is meant to delete only 1 record, meaning if the resulting query with your filters result
to more that 1 record it will 404.


## Controlling who can access the methods

Sileo's Resource class has 2 methods for controlling whether to allow the access of a method or not.

##### `has_perm`
The `has_perm` method is called first before a method is executed. If it returns `False` the resource will throw
a `PermissionDenied` and will not executed the method. The `has_perm` method accepts the `method`
that is the string name of the method that wants to be executed e.g. 'get_pk', 'form_dict', 'filter', 'create', 'update', or 'delete'.

If you want a custom checking for permissions you can either override the `has_perm` method of your resource or add permission functions in the `method_perms` property of your resource.

Here is an example of a resource that requires the users to be authenticated when they access the resource
```python
def login_required(resource, *args, **kwargs):
    request = resource.request
    return hasattr(request, 'user') and request.user.is_authenticated()

class FooResource(Resource):
    query_set = Foo.objects.all()
    allowed_methods = ['filter']
    method_perms = (login_required,)
```
There are common method permission methods available in `sileo.permissions`. Method perm functions should accept the instance of the resource, the method name, and additional arguments passed to the
`has_perm` method and return `True` if permission is given, `False` otherwise.

##### `has_object_perm`
The `has_object_perm` method is called when trying to access the `form_dict` with a filters, `update`, and `delete` methods. If it returns
`False` the resource will raise a `PermissionDenied` and the method will not proceed. The `has_object_perm`
method accepts the `method` name that wants to execute and the `obj` instance that it wants to operate on.

Here is an example of a resource that only allows update and delete methods if the owner of the instance is the currently logged in user.
```python
def owner_required(resource, method, obj, *args, **kwargs):
    user = resource.request.user
    return obj.owner_id == user.id


class FooResource(Resource):
    query_set = Foo.objects.all()
    allowed_methods = ['update', 'delete']
    form_class = FooForm
    update_filter_fields = ('pk',)
    delete_filter_fields = ('pk',)
    method_perms = (login_required,)
    object_perms = (owner_required,)
```

There are common object permission methods available in `sileo.permissions`. Object perm functions should accept the instance of the resource, the method name, the object, and additional arguments passed to the
`has_object_perm` method and return `True` if permission is given, `False` otherwise.
