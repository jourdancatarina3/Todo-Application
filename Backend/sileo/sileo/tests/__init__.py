from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms import ModelForm as DjangoModelForm
from django.conf import settings
from django.conf.urls import url, include

from sileo import registration
from sileo.forms import ModelForm
from sileo.resource import Resource
from sileo.fields import (
    ResourceField, ResourceModel, ResourceModelManager, ResourceQuerySet,
    ResourceGenericModel, ResourceTypeConvert)
from sileo.permissions import login_required, owner_required
from sileo.urls import urlpatterns as sileo_url_patters


class TestUrls(object):
    urlpatterns = (
        url('', include(settings.ROOT_URLCONF)),
        url('sileo-testing-url/', include(
            sileo_url_patters, namespace='sileo-test'))
    )


class SampleApiModel(models.Model):
    title = models.CharField(max_length=50, blank=True)
    owner = models.ForeignKey(User, related_name='samples')
    tagged_user = models.ForeignKey(User, null=True, blank=True)
    target_type = models.ForeignKey(ContentType, null=True, blank=True)
    target_id = models.PositiveIntegerField(null=True)
    target = GenericForeignKey('target_type', 'target_id')
    removed = models.BooleanField(default=False)
    value = models.FloatField(default=0)

    @property
    def owner_samples(self):
        return self.owner.samples.all()


class SampleMiddleWare(object):

    def pre_api_resolve(self, **kwargs):
        pass

    def post_api_resolve(self):
        pass


class SampleUserForm(ModelForm):

    class Meta:
        model = User
        fields = ('username', 'password')


class SampleApiModelForm(ModelForm):

    class Meta:
        model = SampleApiModel
        fields = ('title', 'owner', 'value')


class SampleApiModelFormWithExtraField(ModelForm):
    tagline = forms.CharField(min_length=5)

    class Meta:
        model = SampleApiModel
        fields = ('title', 'owner', 'value')


class SampleApiDjangoModelForm(DjangoModelForm):
    class Meta:
        model = SampleApiModel
        fields = ('title', 'owner', 'value')


class TestUserResource(Resource):
    query_set = User.objects.all()
    fields = ['id', 'first_name', 'last_name']


class TestSampleModelResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', ResourceModel('owner', 'test', 'user')]
    filter_fields = ('id', 'title', 'owner__id')
    allowed_methods = ['get_pk', 'filter']


class TestSampleModelBareResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title']


class TestRequiredFilterFieldsResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', 'owner_id']
    filter_fields = ('id', 'title', 'owner__id')
    required_filter_fields = ('owner__id',)
    allowed_methods = ['filter']


class TestCachedResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', ResourceModel('owner', 'test', 'user')]
    filter_fields = ('id', 'title', 'owner__id')
    allowed_methods = ['get_pk', 'filter']
    cache_prefix = 'sample'
    cache_timeout = 100
    is_cached = True


class TestCachedResourceNoPrefix(TestCachedResource):
    cache_prefix = None


class TestSampleModelCustomFilterResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', ResourceModel('owner', 'test', 'user')]
    filter_fields = ('id', 'title', 'owner__id')
    allowed_methods = ['filter']


class GenericModelSampleModelResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = [ResourceGenericModel(
        'target', {'SampleApiModel': ('test', 'sample_model')})]


class ModelSampleModelResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = [ResourceModel('tagged_user', 'test', 'user')]


class RelatedManagerUserResource(Resource):
    query_set = User.objects.all()
    fields = [ResourceModelManager('samples', 'test', 'sample_bare')]
    filter_fields = ('id',)


class QuerySetSampleModelResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = [ResourceQuerySet('owner_samples', 'test', 'sample_bare')]


class ResourceFieldResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = [ResourceField('owner_samples', 'test', 'sample_bare')]


class ResourceTypeConvertResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', ResourceTypeConvert('value', str)]


class TestGetOnlyUserResource(TestUserResource):
    allowed_methods = ['get_pk']


class TestFilterOnlyUserResource(TestUserResource):
    allowed_methods = ['filter']


class TestCreateOnlyUserResource(TestUserResource):
    allowed_methods = ['create']
    form_class = SampleUserForm


class TestUpdateOnlyUserResource(TestUserResource):
    allowed_methods = ['update']
    form_class = SampleUserForm
    update_filter_fields = ('id', )


class TestDeleteOnlyUserResource(TestSampleModelResource):
    allowed_methods = ['delete']
    delete_filter_fields = ('id', )


class TestFormResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['title', 'value', ResourceModel('owner', 'test', 'user')]
    allowed_methods = ['create', 'update', 'delete', 'form_dict']
    update_filter_fields = ['pk']
    delete_filter_fields = ['pk']
    form_class = SampleApiModelForm


class TestDjangoFormResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', 'value', ResourceModel('owner', 'test', 'user')]
    allowed_methods = ['form_dict']
    form_class = SampleApiDjangoModelForm


class TestNoFormResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', 'value', ResourceModel('owner', 'test', 'user')]
    allowed_methods = ['form_dict']


def disable_get(resource, method, *args, **kwargs):
    return method != 'get_pk'


class TestGetDisabledResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', ResourceModel('owner', 'test', 'user')]
    filter_fields = ('id', 'title', 'owner__id')
    allowed_methods = ['get_pk', 'filter']
    method_perms = (disable_get,)
    form_class = SampleApiModelForm


def disable_filter(resource, method, *args, **kwargs):
    return method != 'filter'


class TestFilterDisabledResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', 'owner_id']
    filter_fields = ('id', 'title', 'owner__id')
    required_filter_fields = ('owner__id',)
    allowed_methods = ['filter']
    method_perms = (disable_filter,)
    form_class = SampleApiModelForm


def disable_create(resource, method, *args, **kwargs):
    return method != 'create'


class TestCreateDisabledResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', 'value', ResourceModel('owner', 'test', 'user')]
    allowed_methods = ['create', 'update', 'delete', 'form_dict']
    update_filter_fields = ['pk']
    method_perms = (disable_create,)
    form_class = SampleApiModelForm


def disable_update(resource, method, obj, *args, **kwargs):
    return method != 'update'


class TestUpdateObjectDisabledResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', 'value', ResourceModel('owner', 'test', 'user')]
    allowed_methods = ['create', 'update', 'delete', 'form_dict']
    update_filter_fields = ['pk']
    object_perms = (disable_update,)
    form_class = SampleApiModelForm


def disable_delete(resource, method, obj, *args, **kwargs):
    return method != 'delete'


class TestDeleteObjectDisabledResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', 'value', ResourceModel('owner', 'test', 'user')]
    allowed_methods = ['create', 'update', 'delete', 'form_dict']
    delete_filter_fields = ['pk']
    object_perms = (disable_delete,)
    form_class = SampleApiModelForm


def disable_form_dict(resource, method, obj, *args, **kwargs):
    return method != 'form_dict'


class TestFormDictDisabledResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', 'value', ResourceModel('owner', 'test', 'user')]
    allowed_methods = ['create', 'update', 'delete', 'form_dict']
    update_filter_fields = ['pk']
    object_perms = (disable_form_dict,)
    form_class = SampleApiModelForm


class TestSampleModelDispatchOverrideResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', ResourceModel('owner', 'test', 'user')]
    update_filter_fields = ['pk']
    allowed_methods = ['get_pk']

    def get_pk(self, pk):
        obj = self.get_instance(pk=pk)
        return self.resolve_fields(obj=obj)


class TestLoginRequiredResource(Resource):
    query_set = SampleApiModel.objects.all()
    method_perms = (login_required,)
    allowed_methods = ['filter']


class TestOwnerRequiredResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['pk']
    allowed_methods = ['delete']
    delete_filter_fields = ('pk',)
    object_perms = (owner_required,)


registration.register('test', 'user', TestUserResource)
registration.register('test', 'user', TestUserResource, version='v2')
registration.register('test', 'cached', TestCachedResource)
registration.register('test', 'cached-no-prefix', TestCachedResourceNoPrefix)
registration.register(
    'test', 'sample_bare', TestSampleModelBareResource)
registration.register(
    'test', 'sample_bare', TestSampleModelBareResource, version='v2')
registration.register(
    'test', 'required_filter', TestRequiredFilterFieldsResource)
registration.register('test', 'sample_model', TestSampleModelResource)
registration.register(
    'test', 'sample_model', TestSampleModelResource, version='v2')
registration.register(
    'test', 'sample_model_custom_filter', TestSampleModelCustomFilterResource)
registration.register(
    'test', 'generic', GenericModelSampleModelResource)
registration.register(
    'test', 'model', ModelSampleModelResource)
registration.register(
    'test', 'related', RelatedManagerUserResource)
registration.register(
    'test', 'queryset', QuerySetSampleModelResource)
registration.register(
    'test', 'resource', ResourceFieldResource)
registration.register(
    'test', 'convert', ResourceTypeConvertResource)
registration.register(
    'test', 'get', TestGetOnlyUserResource)
registration.register(
    'test', 'filter', TestFilterOnlyUserResource)
registration.register(
    'test', 'create', TestCreateOnlyUserResource)
registration.register(
    'test', 'update', TestUpdateOnlyUserResource)
registration.register(
    'test', 'delete', TestDeleteOnlyUserResource)
registration.register(
    'test', 'form', TestFormResource)
registration.register(
    'test', 'django-form', TestDjangoFormResource)
registration.register(
    'test', 'no-form', TestNoFormResource)
registration.register(
    'test', 'get-disabled', TestGetDisabledResource)
registration.register(
    'test', 'filter-disabled', TestFilterDisabledResource)
registration.register(
    'test', 'create-disabled', TestCreateDisabledResource)
registration.register(
    'test', 'update-disabled', TestUpdateObjectDisabledResource)
registration.register(
    'test', 'delete-disabled', TestDeleteObjectDisabledResource)
registration.register(
    'test', 'formdict-disabled', TestFormDictDisabledResource)
registration.register(
    'test', 'dispatch-override', TestSampleModelDispatchOverrideResource)
registration.register(
    'test', 'login_required', TestLoginRequiredResource)
