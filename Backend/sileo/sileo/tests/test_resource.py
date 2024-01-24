# -*- coding:utf-8 -*-
from django.http import Http404
from django.test import TestCase, RequestFactory

from sileo.fields import ResourceModel
from sileo.resource import Resource
from sileo.permissions import login_required
from django.core.exceptions import PermissionDenied
from sileo.tests.factories.user import UserFactory

from sileo.tests import (
    SampleApiModel,
    SampleApiModelForm,
    SampleApiDjangoModelForm)


def disable_update(resource, method, obj, *args, **kwargs):
    return method != 'update'

def disable_delete(resource, method, obj, *args, **kwargs):
    return method != 'delete'

def disable_form_dict(resource, method, obj, *args, **kwargs):
    return method != 'form_dict'


class TestBaseResource(Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', 'value', ResourceModel('owner', 'test', 'user')]
    allowed_methods = ['get_pk', 'filter', 'create', 'update', 'delete', 'form_dict']
    update_filter_fields = ['pk']
    delete_filter_fields = ['pk']
    form_class = SampleApiModelForm


class MethodPermsResource(TestBaseResource):
    method_perms = (login_required,)


class ObjectPermsResource(TestBaseResource):
    object_perms = (disable_update, disable_delete, disable_form_dict)


class WithoutFormResource(TestBaseResource):
    form_class = None


class NotSileoFormResource(TestBaseResource):
    form_class = SampleApiDjangoModelForm


class RequireFilterResource(TestBaseResource):
    filter_fields = ['value']
    required_filter_fields = ['title']


class WithoutFilterDeleteResource(TestBaseResource):
    delete_filter_fields = []


class WithoutUpdateDeleteResource(TestBaseResource):
    delete_filter_fields = []


class CachedResource(TestBaseResource):
    cache_prefix = 'sample'
    cache_timeout = 100
    is_cached = True


class CachedResourceNoPrefix(CachedResource):
    cache_prefix = None


class AllowedMethodsTestResource(TestBaseResource):
    allowed_methods = []


class NoSliceResource(TestBaseResource):
    size_per_request = None


class ResourceTestCase(TestCase):
    """ Test Case for Resource """

    def setUp(self):
        self.user = UserFactory(password='user')
        self.sample1 = SampleApiModel.objects.create(
            owner=self.user, title='sample', value=1.0)
        self.factory = RequestFactory()

    def get_request(self, uri='/api-sileo/ns/name'):
        return self.factory.get(uri)

    def get_request_with_user_login(self):
        request = self.get_request()
        request.user = self.user
        return request

    def test_methods_success(self):
        """ test methods will return success """
        # get_pk
        request_g = self.get_request()
        resource_g = TestBaseResource(request_g)
        result_g = resource_g.dispatch('get_pk', self.sample1.pk)
        self.assertEqual(result_g['status_code'], 200)
        # filter
        request_f = self.get_request()
        resource_f = TestBaseResource(request_f)
        result_f = resource_f.dispatch('filter', {}, top=0, bottom=None)
        self.assertEqual(result_f['status_code'], 200)
        self.assertEqual(len(result_f['data']), 1)
        # form_dict
        request_fd = self.get_request()
        resource_fd = TestBaseResource(request_fd)
        result_fd = resource_fd.dispatch('form_dict', {'pk': self.sample1.pk})
        self.assertEqual(result_fd['status_code'], 200)
        # update
        request_u = self.get_request()
        resource_u = TestBaseResource(request_u)
        data_update = {'title': 'created', 'value': 3.0, 'owner': self.user.pk}
        request_u.POST = data_update
        result_u = resource_u.dispatch('update', {'pk': self.sample1.pk})
        self.assertEqual(result_u['status_code'], 200)
        self.assertEqual(result_u['data']['value'], 3.0)
        # delete
        request_d = self.get_request()
        resource_d = TestBaseResource(request_d)
        result_d = resource_d.dispatch('delete', {'pk': self.sample1.pk})
        self.assertEqual(result_d['status_code'], 200)
        # create
        request_c = self.get_request()
        resource_c = TestBaseResource(request_c)
        data_create = {'title': 'created', 'value': 2.0, 'owner': self.user.pk}
        request_c.POST = data_create
        result_c = resource_c.dispatch('create')
        self.assertEqual(result_c['status_code'], 201)

    def test_dispatch_disallowed_method(self):
        request = self.get_request()
        resource = AllowedMethodsTestResource(request)
        # get_pk
        with self.assertRaises(Http404):
            resource.dispatch('get_pk', self.sample1.pk)
        # filter
        with self.assertRaises(Http404):
            resource.dispatch('filter', {}, top=0, bottom=None)
        # form_dict
        with self.assertRaises(Http404):
            resource.dispatch('form_dict', {'pk': self.sample1.pk})
        # update
        with self.assertRaises(Http404):
            request_u = self.get_request()
            resource_u = AllowedMethodsTestResource(request_u)
            data_update = {'title': 'created', 'value': 3.0, 'owner': self.user.pk}
            request_u.POST = data_update
            resource_u.dispatch('update', {'pk': self.sample1.pk})
        # delete
        with self.assertRaises(Http404):
            resource.dispatch('delete', {'pk': self.sample1.pk})
        # create
        with self.assertRaises(Http404):
            request_c = self.get_request()
            resource_c = AllowedMethodsTestResource(request_c)
            data_create = {'title': 'created', 'value': 2.0, 'owner': self.user.pk}
            request_c.POST = data_create
            resource_c.dispatch('create')

    def test_form_invalid(self):
        """ test post data invalid """
        # create
        request_c = self.get_request()
        resource_c = TestBaseResource(request_c)
        data_create = {'title': 'created', 'value': 1.0}
        request_c.POST = data_create
        result_c = resource_c.dispatch('create')
        self.assertEqual(result_c['status_code'], 400)
        self.assertEqual(len(result_c['data']['owner']), 1)
        # update
        request_u = self.get_request()
        resource_u = TestBaseResource(request_u)
        data_update = {'title': 'created', 'value': 2.0}
        request_u.POST = data_update
        result_u = resource_u.dispatch('update', {'pk': self.sample1.pk})
        self.assertEqual(result_u['status_code'], 400)

    def test_not_sileo_form(self):
        """ test resource's form_class is not sileo Form """
        with self.assertRaises(AttributeError):
            request = self.get_request()
            resource = NotSileoFormResource(request)
            resource.dispatch('form_dict', {'pk': self.sample1.pk})

    def test_method_perms(self):
        """ test method perms for each request method """
        request = self.get_request()
        resource = MethodPermsResource(request)
        # -------- login_required failed
        # get_pk
        with self.assertRaises(PermissionDenied):
            resource.dispatch('get_pk', self.sample1.pk)
        # filter
        with self.assertRaises(PermissionDenied):
            resource.dispatch('filter', {}, top=0, bottom=None)
        # form_dict
        with self.assertRaises(PermissionDenied):
            resource.dispatch('form_dict', {'pk': self.sample1.pk})
        # update
        with self.assertRaises(PermissionDenied):
            request_u = self.get_request()
            resource_u = MethodPermsResource(request_u)
            data_update = {'title': 'created', 'value': 3.0, 'owner': self.user.pk}
            request_u.POST = data_update
            resource_u.dispatch('update', {'pk': self.sample1.pk})
        # delete
        with self.assertRaises(PermissionDenied):
            resource.dispatch('delete', {'pk': self.sample1.pk})
        # create
        with self.assertRaises(PermissionDenied):
            request_c = self.get_request()
            resource_c = MethodPermsResource(request_c)
            data_create = {'title': 'created', 'value': 2.0, 'owner': self.user.pk}
            request_c.POST = data_create
            resource_c.dispatch('create')
        # -------- login_required pass
        # get_pk
        request_g = self.get_request_with_user_login()
        resource_g = MethodPermsResource(request_g)
        result_g = resource_g.dispatch('get_pk', self.sample1.pk)
        self.assertEqual(result_g['status_code'], 200)
        # filter
        request_f = self.get_request_with_user_login()
        resource_f = MethodPermsResource(request_f)
        result_f = resource_f.dispatch('filter', {}, top=0, bottom=None)
        self.assertEqual(result_f['status_code'], 200)
        self.assertEqual(len(result_f['data']), 1)
        # form_dict
        request_fd = self.get_request_with_user_login()
        resource_fd = MethodPermsResource(request_fd)
        result_fd = resource_fd.dispatch('form_dict', {'pk': self.sample1.pk})
        self.assertEqual(result_fd['status_code'], 200)
        # update
        request_u = self.get_request_with_user_login()
        resource_u = MethodPermsResource(request_u)
        data_update = {'title': 'created', 'value': 3.0, 'owner': self.user.pk}
        request_u.POST = data_update
        result_u = resource_u.dispatch('update', {'pk': self.sample1.pk})
        self.assertEqual(result_u['status_code'], 200)
        self.assertEqual(result_u['data']['value'], 3.0)
        # delete
        request_d = self.get_request_with_user_login()
        resource_d = MethodPermsResource(request_d)
        result_d = resource_d.dispatch('delete', {'pk': self.sample1.pk})
        self.assertEqual(result_d['status_code'], 200)
        # create
        request_c = self.get_request_with_user_login()
        resource_c = MethodPermsResource(request_c)
        data_create = {'title': 'created', 'value': 2.0, 'owner': self.user.pk}
        request_c.POST = data_create
        result_c = resource_c.dispatch('create')
        self.assertEqual(result_c['status_code'], 201)

    def test_object_perms(self):
        """ test object perms for unsafe method """
        request = self.get_request()
        resource = ObjectPermsResource(request)
        # disable_update
        with self.assertRaises(PermissionDenied):
            resource.dispatch('update', {'pk': self.sample1.pk})
        # disable_delete
        with self.assertRaises(PermissionDenied):
            resource.dispatch('delete', {'pk': self.sample1.pk})
        # disable_form_dict
        with self.assertRaises(PermissionDenied):
            resource.dispatch('form_dict', {'pk': self.sample1.pk})

    def test_without_form(self):
        """ test without form_class set """
        # create
        with self.assertRaises(ValueError):
            request_c = self.get_request()
            resource_c = WithoutFormResource(request_c)
            data_create = {'title': 'created', 'value': 2.0, 'owner': self.user.pk}
            request_c.POST = data_create
            resource_c.dispatch('create')
        # update
        with self.assertRaises(ValueError):
            request_u = self.get_request()
            resource_u = WithoutFormResource(request_u)
            data_update = {'title': 'created', 'value': 3.0, 'owner': self.user.pk}
            request_u.POST = data_update
            resource_u.dispatch('update', {'pk': self.sample1.pk})
        # form dict
        with self.assertRaises(ValueError):
            request_fd = self.get_request()
            resource_fd = WithoutFormResource(request_fd)
            resource_fd.dispatch('form_dict', {'pk': self.sample1.pk})

    def test_filters(self):
        """ test filters """
        # without filters
        with self.assertRaises(Http404):
            request1 = self.get_request()
            resource1 = RequireFilterResource(request1)
            resource1.dispatch('filter', {}, top=0, bottom=None)
        # without required filters
        with self.assertRaises(Http404):
            request2 = self.get_request()
            resource2 = RequireFilterResource(request2)
            resource2.dispatch('filter', {'test': 'value'}, top=0, bottom=1)
        # with required filters
        request3 = self.get_request()
        resource3 = RequireFilterResource(request3)
        result3 = resource3.dispatch(
            'filter', {'title': 'sample'}, top=0, bottom=None)
        self.assertEqual(result3['status_code'], 200)
        self.assertEqual(len(result3['data']), 1)
        # with optional filters
        request4 = self.get_request()
        resource4 = RequireFilterResource(request4)
        result4 = resource4.dispatch(
            'filter', {'title': 'sample', 'value': -22}, top=0, bottom=None)
        self.assertEqual(result4['status_code'], 200)
        self.assertEqual(len(result4['data']), 0)
        # without delete filters
        with self.assertRaises(Http404):
            request5 = self.get_request()
            resource5 = WithoutFilterDeleteResource(request5)
            resource5.dispatch('delete', {})
        # without update filters
        with self.assertRaises(Http404):
            request6 = self.get_request()
            resource6 = WithoutUpdateDeleteResource(request6)
            resource6.dispatch('update', {})

    def test_filter_no_instance(self):
        """ test filters without data matched """
        # update
        with self.assertRaises(Http404):
            request_u = self.get_request()
            resource_u = TestBaseResource(request_u)
            data_update = {'title': 'created', 'value': 3.0, 'owner': self.user.pk}
            request_u.POST = data_update
            resource_u.dispatch('update', {'pk': self.sample1.pk+100})
        # delete
        with self.assertRaises(Http404):
            request_d = self.get_request()
            resource_d = TestBaseResource(request_d)
            resource_d.dispatch('delete', {'pk': self.sample1.pk+100})

    def test_cache_with_prefix(self):
        """ test cache with key prefix """
        # get_pk
        request_g = self.get_request()
        resource_g = CachedResource(request_g)
        result_g = resource_g.dispatch('get_pk', self.sample1.pk)
        self.assertEqual(result_g['status_code'], 200)
        # filter
        request_f = self.get_request()
        resource_f = CachedResource(request_f)
        result_f = resource_f.dispatch('filter', {}, top=0, bottom=None)
        self.assertEqual(result_f['status_code'], 200)
        self.assertEqual(len(result_f['data']), 1)
        # update - no cache
        request_u = self.get_request()
        resource_u = CachedResource(request_u)
        data_update = {'title': 'created', 'value': 3.0, 'owner': self.user.pk}
        request_u.POST = data_update
        result_u = resource_u.dispatch('update', {'pk': self.sample1.pk})
        self.assertEqual(result_u['status_code'], 200)
        self.assertEqual(result_u['data']['value'], 3.0)

    def test_cache_without_prefix(self):
        """ test cache without key prefix """
        # get_pk
        request_g = self.get_request()
        resource_g = CachedResourceNoPrefix(request_g)
        result_g = resource_g.dispatch('get_pk', self.sample1.pk)
        self.assertEqual(result_g['status_code'], 200)
        # filter
        request_f = self.get_request()
        resource_f = CachedResourceNoPrefix(request_f)
        result_f = resource_f.dispatch('filter', {}, top=0, bottom=None)
        self.assertEqual(result_f['status_code'], 200)
        self.assertEqual(len(result_f['data']), 1)

    def test_resource_with_none_size_per_request(self):
        # create a lot of instances
        for i in range(0, 20):
            SampleApiModel.objects.create(
                owner=self.user, title='sample', value=1.0)

        # filter
        request_f = self.get_request()
        resource_f = NoSliceResource()
        result_f = resource_f.dispatch('filter', {})
        self.assertEqual(result_f['status_code'], 200)
        self.assertEqual(len(result_f['data']), SampleApiModel.objects.count())
