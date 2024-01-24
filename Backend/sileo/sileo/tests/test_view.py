import json

import django
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test import TestCase, Client
from django.test.utils import override_settings

from sileo import registration

from sileo.tests import (SampleApiModel, SampleApiModelForm, TestUrls)
from sileo.tests import (TestSampleModelResource)
from sileo.tests.factories.user import UserFactory


TEST_API_MIDDLEWARE = ['sileo.tests.SampleMiddleWare']


@override_settings(API_MIDDLEWARE=TEST_API_MIDDLEWARE, ROOT_URLCONF=TestUrls)
class ApiAllowedMethodsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = UserFactory(password='user')
        self.sample_obj = SampleApiModel.objects.create(owner=self.user)

    def test_get_only(self):
        """ Test api resource that only allows get queries """
        response = self.client.get(
            reverse('sileo-test:api-detail', args=(
                'test', 'get', self.user.pk)),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        response_filter = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'get')),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_filter.status_code, 404)
        response_create = self.client.post(
            reverse('sileo-test:api-create', args=('test', 'get')),
            {'username': 'user1', 'password': 'test1'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_create.status_code, 404)
        response_update = self.client.post(
            reverse('sileo-test:api-update', args=('test', 'get')) +
            "?id={}".format(self.user.id),
            {'username': 'user1', 'password': 'test1'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_update.status_code, 404)
        response_delete = self.client.post(
            reverse('sileo-test:api-delete', args=('test', 'get')) +
            "?id={}".format(self.sample_obj.pk),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_delete.status_code, 404)

    def test_filter_only(self):
        """ Test api resource that only allows filter queries """
        response = self.client.get(
            reverse('sileo-test:api-detail',
                    args=('test', 'filter', self.user.pk)),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)
        response_filter = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'filter')),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_filter.status_code, 200)
        response_create = self.client.post(
            reverse('sileo-test:api-create', args=('test', 'filter')),
            {'username': 'user1', 'password': 'test1'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_create.status_code, 404)
        response_update = self.client.post(
            reverse('sileo-test:api-update', args=('test', 'filter')) +
            "?id={}".format(self.user.id),
            {'username': 'user1', 'password': 'test1'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_update.status_code, 404)
        response_delete = self.client.post(
            reverse('sileo-test:api-delete', args=('test', 'filter')) +
            '?id={}'.format(self.sample_obj.pk),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_delete.status_code, 404)

    def test_create_only(self):
        """ Test api resource that only allows create queries """
        response = self.client.get(
            reverse('sileo-test:api-detail',
                    args=('test', 'create', self.user.pk)),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)
        response_filter = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'create')),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_filter.status_code, 404)
        response_create = self.client.post(
            reverse('sileo-test:api-create', args=('test', 'create')),
            {'username': 'user1', 'password': 'test1'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_create.status_code, 201)
        self.assertEqual(User.objects.count(), 2)
        response_update = self.client.post(
            reverse('sileo-test:api-update', args=('test', 'create')) +
            "?id={}".format(self.user.id),
            {'username': 'user1', 'password': 'test1'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_update.status_code, 404)
        response_delete = self.client.post(
            reverse('sileo-test:api-delete', args=('test', 'create')) +
            '?id={}'.format(self.sample_obj.pk),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_delete.status_code, 404)

    def test_update_only(self):
        """ Test api resource that only allows update queries """
        response = self.client.get(
            reverse('sileo-test:api-detail',
                    args=('test', 'update', self.user.pk)),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)
        response_filter = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'update')),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_filter.status_code, 404)
        response_create = self.client.post(
            reverse('sileo-test:api-create', args=('test', 'update')),
            {'username': 'user1', 'password': 'test1'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_create.status_code, 404)
        response_update = self.client.post(
            reverse('sileo-test:api-update', args=('test', 'update')) +
            "?id={}".format(self.user.pk),
            {'username': 'user1', 'password': 'test1'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_update.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        response_delete = self.client.post(
            reverse('sileo-test:api-delete', args=('test', 'update')) +
            '?id={}'.format(self.sample_obj.pk),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_delete.status_code, 404)

    def test_delete_only(self):
        """ Test api resource that only allows delete queries """
        response = self.client.get(
            reverse('sileo-test:api-detail',
                    args=('test', 'delete', self.user.pk)),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)
        response_filter = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'delete')),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_filter.status_code, 404)
        response_create = self.client.post(
            reverse('sileo-test:api-create', args=('test', 'delete')),
            {'username': 'user1', 'password': 'test1'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_create.status_code, 404)
        response_update = self.client.post(
            reverse('sileo-test:api-update', args=('test', 'delete')) +
            "?id={}".format(self.user.id),
            {'username': 'user1', 'password': 'test1'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_update.status_code, 404)
        response_delete = self.client.post(
            reverse('sileo-test:api-delete', args=('test', 'delete')) +
            '?id={}'.format(self.sample_obj.pk),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response_delete.status_code, 200)


@override_settings(ROOT_URLCONF=TestUrls)
class APIGetTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = UserFactory(password='user')
        self.sample = SampleApiModel.objects.create(
            title='test', owner=self.user)
        try:
            registration.register(
                'test', 'sample', TestSampleModelResource)
        except KeyError:
            pass
        resource_type = registration.get_resource('test', 'sample')
        self.resource = resource_type()

    def test_get(self):
        """ Test model's get method. """
        output = {'status_code': 200, 'data': self.resource.resolve_fields(
            self.sample)}
        self.assertEqual(self.resource.get_pk(self.sample.pk), output)
        self.assertEqual(
            self.resource.get_cache_key(1), 'TestSampleModelResource_1')

    def test_get_object_does_not_exist(self):
        """ Test model's get method with a pk that does not exist. """
        self.assertRaises(Http404, self.resource.get_pk, 100)

    def test_get_request(self):
        """ Test api get using HTTP request. """
        response = self.client.get(
            reverse('sileo-test:api-detail', args=(
                'test', 'sample-not-found', self.sample.pk)),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)
        response = self.client.get(
            reverse('sileo-test:api-detail',
                    args=('test', 'sample', self.sample.pk)),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        objects = json.loads(response.content)
        self.assertEqual(
            self.resource.resolve_fields(self.sample), objects['data'])

    def test_get_disabled(self):
        response = self.client.get(
            reverse('sileo-test:api-detail',
                    args=('test', 'get-disabled', self.sample.pk)),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)


@override_settings(ROOT_URLCONF=TestUrls)
class ApiFilterTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory(password='user')
        self.user2 = UserFactory(password='user2')
        self.sample1 = SampleApiModel.objects.create(
            owner=self.user, title='sample')
        self.sample2 = SampleApiModel.objects.create(
            owner=self.user, title='sample')
        self.sample3 = SampleApiModel.objects.create(
            owner=self.user2, title='sample')
        self.user_resource = registration.get_resource(
            'test', 'user')()
        self.sample_model_resource = registration.get_resource(
            'test', 'sample_model')()
        self.cached_model_resource = registration.get_resource(
            'test', 'cached')()
        self.client = Client()

    def test_filter_no_args(self):
        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'sample_model')),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        samples = SampleApiModel.objects.all()[
            0:self.sample_model_resource.size_per_request].count()
        objects = json.loads(response.content)
        self.assertEqual(len(objects['data']), samples)

    def test_filter_args(self):
        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'sample_model')) +
            '?id={}'.format(self.sample1.pk),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        expected = [self.sample_model_resource.resolve_fields(self.sample1)]
        objects = json.loads(response.content)
        self.assertEqual(objects['data'], expected)

    def test_filter_multiple_args(self):
        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'sample_model')) +
            '?id={}&owner__id={}'.format(self.sample2.pk, self.user.pk),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        expected = [self.sample_model_resource.resolve_fields(self.sample2)]
        objects = json.loads(response.content)
        self.assertEqual(objects['data'], expected)

    def test_filter_multiple_args_none_found(self):
        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'sample_model')) +
            '?id={}&title={}'.format(self.sample1.pk, 'here'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        expected = []
        objects = json.loads(response.content)
        self.assertEqual(objects['data'], expected)

    def test_filter_zero_args(self):
        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'sample_model')) +
            '?id=0&owner__id=-1', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        expected = []
        objects = json.loads(response.content)
        self.assertEqual(objects['data'], expected)

    def test_filter_cached(self):
        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'cached')) +
            '?id={}'.format(self.sample1.pk),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        expected = [self.sample_model_resource.resolve_fields(self.sample1)]
        objects = json.loads(response.content)
        self.assertEqual(objects['data'], expected)

        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'cached')) +
            '?id={}'.format(self.sample1.pk),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        expected = [self.sample_model_resource.resolve_fields(self.sample1)]
        objects = json.loads(response.content)
        self.assertListEqual(objects['data'], expected)

    def test_filter_with_slice(self):
        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'sample_model')) +
            '?top=1',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        expected = len(SampleApiModel.objects.all()[
                       1:1 + self.sample_model_resource.size_per_request])
        objects = json.loads(response.content)
        self.assertEqual(len(objects['data']), expected)

    def test_custom_filter(self):
        """ Test api resource with custom filter method """
        response = self.client.get(
            reverse('sileo-test:api-list',
                    args=('test', 'sample_model_custom_filter')) +
            '?top=1',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        expected = len(SampleApiModel.objects.all()[1:11])
        objects = json.loads(response.content)
        self.assertEqual(len(objects['data']), expected)
        response2 = self.client.get(
            reverse('sileo-test:api-list',
                    args=('test', 'sample_model_custom_filter')) +
            '?id={}'.format(self.sample2.pk),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        objects2 = json.loads(response2.content)
        self.assertEqual(len(objects2['data']), 1)

    def test_size_per_request(self):
        """ Test filter on a database with records more than the
            size_per_request
        """
        for i in xrange(0, 20):
            SampleApiModel.objects.create(owner=self.user2, title='sample3')
        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'sample_model')) +
            '?top=1',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        objects = json.loads(response.content)
        self.assertEqual(
            len(objects['data']), self.sample_model_resource.size_per_request)

    def test_bottom_arg(self):
        """ Test api with valid bottom argument """
        for i in xrange(0, 20):
            SampleApiModel.objects.create(owner=self.user2, title='sample3')
        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'sample_model')) +
            '?top=0&bottom=5',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        objects = json.loads(response.content)
        self.assertEqual(len(objects['data']), 5)

    def test_negative_bottom_arg(self):
        """ Test api with negative bottom argument """
        for i in xrange(0, 20):
            SampleApiModel.objects.create(owner=self.user2, title='sample3')
        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'sample_model')) +
            '?top=1&bottom=-12',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        objects = json.loads(response.content)
        self.assertEqual(
            len(objects['data']), self.sample_model_resource.size_per_request)

    def test_with_required_filter(self):
        """ Test api with required filter """
        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'required_filter')) +
            '?top=0&bottom=6&owner__id={}'.format(self.user.id),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        objects = json.loads(response.content)
        self.assertEqual(len(objects['data']), 2)

        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'required_filter')) +
            '?top=0&bottom=6&owner__id={}&id={}'.format(
                self.user.id, self.sample1.id),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        objects = json.loads(response.content)
        self.assertEqual(len(objects['data']), 1)

        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'required_filter')) +
            '?top=0&bottom=6&owner__id={}&title={}'.format(
                self.user2.id, 'sample'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        objects = json.loads(response.content)
        self.assertEqual(len(objects['data']), 1)
        self.assertEqual(objects['data'][0]['id'], self.sample3.id)

    def test_without_required_filter(self):
        """ Test api with lacking required filter """
        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'required_filter')) +
            '?top=0&bottom=6&title={}'.format('sample'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'required_filter')),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

    def test_filter_disabled(self):
        response = self.client.get(
            reverse('sileo-test:api-list', args=('test', 'filter-disabled')) +
            '?top=0&bottom=6&owner__id={}'.format(self.user.id),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)


@override_settings(ROOT_URLCONF=TestUrls)
class ResourceFormTestCase(TestCase):
    """ Test Case for form related api accesses """

    def setUp(self):
        self.user = UserFactory(password='user')
        self.sample1 = SampleApiModel.objects.create(
            owner=self.user, title='sample', value=1.0)
        self.resource = registration.get_resource(
            'test', 'form')()

    def test_create_success(self):
        """ Test api resource success create """
        response = self.client.post(
            reverse('sileo-test:api-create', args=('test', 'form')),
            {'title': 'created', 'value': 2.0, 'owner': self.user.pk},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SampleApiModel.objects.count(), 2)
        self.assertEqual(SampleApiModel.objects.last().title, 'created')
        objects = json.loads(response.content)
        self.assertEqual(objects['data']['title'], 'created')

    def test_create_invalid(self):
        """ Test api resource invalid create """
        response = self.client.post(
            reverse('sileo-test:api-create', args=('test', 'form')),
            {'title': 'created', 'value': 2.0},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(SampleApiModel.objects.count(), 1)
        objects = json.loads(response.content)
        self.assertIn('owner', objects['data'])

    def test_update_success(self):
        """ Test api resource success update """
        response = self.client.post(
            reverse('sileo-test:api-update', args=('test', 'form')) +
            '?pk={}'.format(self.sample1.pk),
            {'title': 'updated', 'value': 3.0, 'owner': self.user.pk},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SampleApiModel.objects.count(), 1)
        self.assertEqual(SampleApiModel.objects.last().title, 'updated')
        objects = json.loads(response.content)
        self.assertEqual(objects['data']['title'], 'updated')

    def test_update_invalid(self):
        """ Test api resource invalid update """
        response = self.client.post(
            reverse('sileo-test:api-update', args=('test', 'form')) +
            '?pk={}'.format(self.sample1.pk),
            {'title': 'updated', 'value': 3.0},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(SampleApiModel.objects.count(), 1)
        objects = json.loads(response.content)
        self.assertIn('owner', objects['data'])

    def test_delete_success(self):
        """ Test api resource success delete """
        response = self.client.post(
            reverse('sileo-test:api-delete', args=('test', 'form')) +
            '?pk={}'.format(self.sample1.pk),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SampleApiModel.objects.filter(
            removed=True).count(), 1)
        objects = json.loads(response.content)
        self.assertEqual(objects['data']['pk'], self.sample1.pk)

    def test_form_info(self):
        """ Test api resource form info success """
        response = self.client.get(
            reverse('sileo-test:api-form-info', args=('test', 'form')),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        expected = {'data': SampleApiModelForm({}).as_dict()}
        objects = json.loads(response.content)
        self.assertEqual(objects['data']['title'], expected['data']['title'])

    def test_form_info_with_instance(self):
        """ Test api resource form info with instance success """
        response = self.client.get(
            reverse('sileo-test:api-form-info', args=('test', 'form')) +
            '?pk={}'.format(self.sample1.pk),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        expected = {'data': SampleApiModelForm({}).as_dict()}
        objects = json.loads(response.content)
        self.assertEqual(objects['data']['title'], expected['data']['title'])

    @override_settings(LOGGING={})
    def test_form_info_django_form(self):
        """ Test api resource with django form set """
        django.setup()
        with self.assertRaises(AttributeError):
            self.client.get(
                reverse('sileo-test:api-form-info',
                        args=('test', 'django-form')),
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    @override_settings(LOGGING={})
    def test_form_info_no_form(self):
        """ Test api resource no form class set """
        django.setup()
        with self.assertRaises(ValueError):
            self.client.get(
                reverse('sileo-test:api-form-info', args=('test', 'no-form')),
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    def test_create_disabled(self):
        """ Test api resource disabled object create"""
        response = self.client.post(
            reverse('sileo-test:api-create', args=('test', 'create-disabled')),
            {'title': 'created', 'value': 3.0, 'owner': self.user.pk},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

    def test_update_disabled(self):
        """ Test api resource disabled object update """
        response = self.client.post(
            reverse('sileo-test:api-update',
                    args=('test', 'update-disabled')) +
            '?pk={}'.format(self.sample1.pk),
            {'title': 'updated', 'value': 3.0, 'owner': self.user.pk},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

    def test_delete_disabled(self):
        """ Test api resource disabled object delete """
        response = self.client.post(
            reverse('sileo-test:api-delete',
                    args=('test', 'delete-disabled')) +
            '?pk={}'.format(self.sample1.pk),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

    def test_form_dict_disabled(self):
        """ Test api resource disabled object form_dict """
        response = self.client.get(
            reverse('sileo-test:api-form-info',
                    args=('test', 'formdict-disabled')) +
            '?pk={}'.format(self.sample1.pk),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)


@override_settings(ROOT_URLCONF=TestUrls)
class IncorrectDispatchTestCase(TestCase):
    """ Test Case for incorrect return value of dispatch create function"""

    def setUp(self):
        self.user = UserFactory(password='user')
        self.sample1 = SampleApiModel.objects.create(
            owner=self.user, title='sample', value=1.0)
        self.resource = registration.get_resource(
            'test', 'dispatch-override')()

    def test_get_only_incorrect_dispatch_get_override(self):
        """ Test api resource with incorrect create function override """
        response = self.client.get(
            reverse('sileo-test:api-detail', args=(
                'test', 'dispatch-override', self.sample1.pk)),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)


@override_settings(
    ROOT_URLCONF=TestUrls,
    SILEO_API_FALLBACK_VERSION='v1',
    SILEO_ALLOWED_VERSIONS=('v1', 'v2'))
class VersionedUrlTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = UserFactory(password='user')
        self.sample = SampleApiModel.objects.create(
            title='test', owner=self.user)
        try:
            registration.register(
                'test', 'sample', TestSampleModelResource)
        except KeyError:
            pass
        try:
            registration.register(
                'test', 'sample', TestSampleModelResource, version='v2')
        except KeyError:
            pass
        resource_type = registration.get_resource('test', 'sample')
        self.resource = resource_type()
        self.resource2 = registration.get_resource(
            'test', 'sample', version='v2')()

    def test_versioned_url(self):
        """ Test views versioned and non-versioned urls. """
        response1 = self.client.get(
            reverse('sileo-test:api-detail',
                    args=('test', 'sample', self.sample.pk)),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response1.status_code, 200)
        objects1 = json.loads(response1.content)
        self.assertEqual(
            self.resource.resolve_fields(self.sample), objects1['data'])

        response2 = self.client.get(
            reverse('sileo-test:api-detail-version',
                    args=('v1', 'test', 'sample', self.sample.pk)),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response2.status_code, 200)
        objects2 = json.loads(response2.content)
        self.assertEqual(
            self.resource.resolve_fields(self.sample), objects2['data'])

        response3 = self.client.get(
            reverse('sileo-test:api-detail-version',
                    args=('v2', 'test', 'sample', self.sample.pk)),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response3.status_code, 200)
        objects3 = json.loads(response3.content)
        self.assertEqual(
            self.resource2.resolve_fields(self.sample), objects3['data'])
        self.assertEqual(objects1, objects3)
