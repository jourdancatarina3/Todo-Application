from time import sleep
import uuid

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test.utils import override_settings

from django.test import TestCase

from sileo import registration
from sileo import mixins
from sileo import permissions
from sileo.resource import Resource
from sileo.fields import ResourceModel
from sileo.tests.factories.user import UserFactory
from sileo.tests import SampleApiModel, TestUrls


TEST_API_MIDDLEWARE = ['sileo.tests.SampleMiddleWare']


class TestLoginRequiredMixinResource(mixins.LoginRequiredMixin, Resource):
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', 'value', ResourceModel('owner', 'test', 'user')]
    allowed_methods = ['filter']
    method_perms = (permissions.login_required,)

registration.register('test', 'login-required-mixin',
                      TestLoginRequiredMixinResource)


@override_settings(ROOT_URLCONF=TestUrls)
class LoginRequiredMixinTestCase(TestCase):
    def setUp(self):
        self.password = '123'
        self.user = UserFactory(password=self.password)
        self.sample = SampleApiModel.objects.create(
            owner=self.user, title='sample', value=1.0
        )

    def test_login_required_mixin_not_login(self):
        """Get resource with not login"""
        response = self.client.get(
            reverse('sileo-test:api-list',
                    args=('test', 'login-required-mixin')),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

    def test_login_required_mixin_login(self):
        """Get resource with login success"""
        self.client.login(username=self.user.username,
                          password=self.password)
        response = self.client.get(
            reverse('sileo-test:api-list',
                    args=('test', 'login-required-mixin')),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)


def make_fake_request(user=None):
    class FakeRequest(object):

        def __init__(self, user=None):
            self.user = User.objects.create_user(
                username=uuid.uuid4().__str__()[:30], password='fakeuser')

    return FakeRequest(user)


def raise_value_error(cache_key):
    raise ValueError


class RateLimitedResource(mixins.RateLimitMixin, Resource):
    query_set = User.objects.all()
    ratelimit_methods = ['filter', 'get_pk']
    allowed_methods = ['get_pk']
    ratelimit_rate = '1/1'


class RateLimitMixinTestCase(TestCase):
    def setUp(self):
        self.fake_request = make_fake_request()

    def test_get_rate_limit_key(self):
        rt = RateLimitedResource(self.fake_request)
        self.assertEqual(self.fake_request.user.pk, rt.get_rate_limit_key())

    def test_get_rate_limit_cache_key(self):
        rt = RateLimitedResource(self.fake_request)
        expected = 'sileo_ratelimit_RateLimitedResource_filter_%r' % \
                   self.fake_request.user.pk
        self.assertEqual(expected, rt._get_rate_limit_cache_key('filter'))

    def test_get_rate(self):
        rt = RateLimitedResource(self.fake_request)
        self.assertEqual([1, 1], rt._get_rate())

    def test_error_data(self):
        rt = RateLimitedResource(self.fake_request)
        data = rt.error_data()
        self.assertIn('status_code', data)
        self.assertIn('data', data)

    def test_check_allowed_by_limit(self):
        rt = RateLimitedResource(self.fake_request)
        self.assertTrue(rt._check_allowed_by_limit('filter'))
        self.assertFalse(rt._check_allowed_by_limit('filter'))
        sleep(1)
        self.assertTrue(rt._check_allowed_by_limit('filter'))
        self.assertTrue(rt._check_allowed_by_limit('get_pk'))
        self.assertFalse(rt._check_allowed_by_limit('filter'))
        self.assertTrue(rt._check_allowed_by_limit('update'))
        self.assertTrue(rt._check_allowed_by_limit('update'))
        self.assertTrue(rt._check_allowed_by_limit('update'))

        from mock import patch
        sleep(1)
        with patch('django.core.cache.cache.decr', raise_value_error):
            self.assertTrue(rt._check_allowed_by_limit('filter'))
            self.assertTrue(rt._check_allowed_by_limit('filter'))

    def test_dispatch(self):
        rt = RateLimitedResource(self.fake_request)
        self.assertEqual(
            200,
            rt.dispatch('get_pk', self.fake_request.user.pk)['status_code'])
        self.assertEqual(
            403,
            rt.dispatch('get_pk', self.fake_request.user.pk)['status_code'])


class MethodLoginRequiredResource(mixins.MethodLoginRequiredMixin, Resource):
    """resource for test `mixins.MethodLoginRequiredMixin`"""
    query_set = SampleApiModel.objects.all()
    fields = ['id', 'title', 'value', ResourceModel('owner', 'test', 'user')]
    allowed_methods = ['filter', 'get_pk']

    login_required_methods = ['filter']

registration.register('test', 'method-login-required-mixin',
                      MethodLoginRequiredResource)


@override_settings(ROOT_URLCONF=TestUrls)
class MethodLoginRequiredTestCase(TestCase):
    def setUp(self):
        self.password = '123'
        self.user = UserFactory(password=self.password)
        self.sample = SampleApiModel.objects.create(
            owner=self.user, title='sample', value=1.0
        )

    def test_login_required_method_not_login(self):
        """Get resource with not login"""
        response = self.client.get(
            reverse('sileo-test:api-list',
                    args=('test', 'method-login-required-mixin')),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 403)

    def test_not_login_required_method_not_login(self):
        """Get resource detail with not login and success"""
        pk = self.sample.pk
        response = self.client.get(
            reverse('sileo-test:api-detail',
                    args=('test', 'method-login-required-mixin', pk)),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)

    def test_login_required_method_login(self):
        """Get resource with login"""
        self.client.login(username=self.user.username,
                          password=self.password)
        response = self.client.get(
            reverse('sileo-test:api-list',
                    args=('test', 'method-login-required-mixin')),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
