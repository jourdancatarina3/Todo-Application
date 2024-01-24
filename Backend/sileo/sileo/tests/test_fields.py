# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from sileo.resource import Resource
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from sileo.fields import (
    ResourceField, ResourceModel, ResourceModelManager, ResourceQuerySet,
    ResourceGenericModel, ResourceTypeConvert, ResourceMethodField)
from sileo.tests.factories.user import UserFactory
from sileo.tests import (
    SampleApiModel,
    SampleApiModelForm,
    SampleApiDjangoModelForm)


class OwnerIsOptionalModel(models.Model):
    title = models.CharField(max_length=50, blank=True)
    owner = models.ForeignKey(User, related_name='samples2',
                              null=True, blank=True)
    value = models.FloatField(default=0)

    class Meta:
        app_label = 'core'


class TestBaseResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', 'value',
              ResourceMethodField('customfield', method_name='get_custom_field'),
              ResourceMethodField('default_field')]

    def get_custom_field(self, prop, obj, request):
        return 'hello world'

    def get_default_field(self, prop, obj, request):
        return 'default field'


class FaultyMethodFieldResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = [ResourceMethodField('no_field')]


class FieldsBaseTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory(password='user')
        self.sample1 = SampleApiModel.objects.create(
            owner=self.user, title='sample', value=1.0)
        self.factory = RequestFactory()

    def get_request(self, uri='/api-sileo/ns/name'):
        return self.factory.get(uri)


class ResourceMethodFieldTestCase(FieldsBaseTestCase):

    def test_resolve_fields(self):
        resource = TestBaseResource()
        context = resource.resolve_fields(self.sample1)
        self.assertIn('customfield', context)
        self.assertEqual('hello world', context['customfield'])
        self.assertIn('default_field', context)
        self.assertEqual('default field', context['default_field'])

    def test_resolve_faulty_field(self):
        resource = FaultyMethodFieldResource()
        with self.assertRaises(AttributeError):
            resource.resolve_fields(self.sample1)


class ResourceFieldTestCase(FieldsBaseTestCase):
    """ Base Resource field class test """

    def test_resolve(self):
        resource_field = ResourceField('owner', 'test', 'user')
        request = self.get_request()
        result = resource_field.resolve(self.sample1, request)
        self.assertEqual(result, None)

    def test_resolve_class(self):
        resource_field = ResourceField('owner', 'test', 'user')
        self.assertEqual(resource_field.resolver_class.__name__,
                         'TestUserResource')


class ResourceModelTestCase(FieldsBaseTestCase):
    """ ResourceModel Test Case """

    def setUp(self):
        super(ResourceModelTestCase, self).setUp()
        self.sample2 = OwnerIsOptionalModel.objects.create(
            owner=None, title='sample', value=1.0)

    def test_resolve(self):
        resource_model = ResourceModel('owner', 'test', 'user')
        request = self.get_request()
        result = resource_model.resolve(self.sample1, request)
        self.assertEqual(
            result, {
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'id': self.user.id,
            })
        # without related owner
        result2 = resource_model.resolve(self.sample2, request)
        self.assertEqual(result2, None)


class ResourceModelManagerTestCase(FieldsBaseTestCase):
    """ ResourceModelManager Test Case """

    def test_resolve(self):
        resource_model = ResourceModelManager(
            'owner_samples', 'test', 'sample_bare')
        request = self.get_request()
        result = resource_model.resolve(self.sample1, request)
        self.assertEqual(len(result), 1)


class ResourceQuerySetTestCase(FieldsBaseTestCase):
    """ ResourceQuerySet Test Case """

    def test_resolve(self):
        resource_model = ResourceQuerySet(
            'owner_samples', 'test', 'sample_bare')
        request = self.get_request()
        result = resource_model.resolve(self.sample1, request)
        self.assertEqual(len(result), 1)


class ResourceGenericModelTestCase(FieldsBaseTestCase):
    """ ResourceGenericModel Test Case """

    def setUp(self):
        super(ResourceGenericModelTestCase, self).setUp()
        self.traget_model = SampleApiModel.objects.create(
            owner=self.user, title='sample', value=2.0)
        self.sample2 = SampleApiModel.objects.create(
            owner=self.user, title='sample2', value=3.0,
            target=self.traget_model)

    def test_resolve(self):
        # no target model
        resource_model = ResourceGenericModel(
            'target', {'SampleApiModel': ('test', 'sample_model')})
        request = self.get_request()
        result = resource_model.resolve(self.sample1, request)
        self.assertEqual(result, None)
        # with target model
        result2 = resource_model.resolve(self.sample2, request)
        self.assertEqual(result2['id'], self.traget_model.id)


class ResourceTypeConvertManagerTestCase(FieldsBaseTestCase):
    """ ResourceTypeConvertManager Test Case """

    def test_resolve(self):
        resource_model = ResourceTypeConvert('value', str)
        request = self.get_request()
        result = resource_model.resolve(self.sample1, request)
        self.assertEqual(result, str(self.sample1.value))

    def test_resolve_with_null_values(self):
        resource_model = ResourceTypeConvert('target_id', str)
        request = self.get_request()
        result = resource_model.resolve(self.sample1, request)
        self.assertIsNone(result)


class ResourceFieldVersionedTestCase(FieldsBaseTestCase):

    def setUp(self):
        super(ResourceFieldVersionedTestCase, self).setUp()
        self.target_model = SampleApiModel.objects.create(
            owner=self.user, title='sample', value=2.0)
        self.sample2 = SampleApiModel.objects.create(
            owner=self.user, title='sample2', value=3.0,
            target=self.target_model)
        self.sample3 = OwnerIsOptionalModel.objects.create(
            owner=self.user, title='sample', value=1.0)

    def test_resolve_generic_model(self):
        resource_model = ResourceGenericModel(
            'target', {'SampleApiModel': ('test', 'sample_model', 'v2')})
        request = self.get_request()
        result = resource_model.resolve(self.sample2, request)
        self.assertEqual(result['id'], self.target_model.id)

    def test_resolve_query_set(self):
        resource_model = ResourceQuerySet(
            'owner_samples', 'test', 'sample_bare', version='v2')
        request = self.get_request()
        result = resource_model.resolve(self.sample1, request)
        self.assertEqual(len(result), 3)

    def test_resolve_model_manager(self):
        resource_model = ResourceModelManager(
            'owner_samples', 'test', 'sample_bare', 'v2')
        request = self.get_request()
        result = resource_model.resolve(self.sample1, request)
        self.assertEqual(len(result), 3)

    def test_resolve_field(self):
        resource_field = ResourceField('owner', 'test', 'user', version='v2')
        request = self.get_request()
        result = resource_field.resolve(self.sample2, request)
        self.assertEqual(result, None)

    def test_resolve_model(self):
        resource_model = ResourceModel('owner', 'test', 'user', version='v2')
        request = self.get_request()
        result = resource_model.resolve(self.sample3, request)
        self.assertEqual(
            result, {
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'id': self.user.id,
            })
