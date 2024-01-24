from django.core.urlresolvers import reverse
from django.test import TestCase

from sileo import registration
from sileo.resource import Resource
from sileo.tests.factories.user import UserFactory
from sileo.tests import TestUrls
from sileo.permissions import login_required, owner_required
from django.test.utils import override_settings

from sileo.tests import SampleApiModel


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


registration.register(
    'test', 'login-required-perms', TestLoginRequiredResource)
registration.register(
    'test', 'owner-required-perms', TestOwnerRequiredResource)


@override_settings(ROOT_URLCONF=TestUrls)
class LoginRequiredTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(password='123')
        self.sample1 = SampleApiModel.objects.create(
            owner=self.user, title='sample', value=1.0)

    def test_login_required_authenticated(self):
        self.client.login(
            username=self.user.username, password='123')
        response = self.client.get(
            reverse('sileo-test:api-list', args=(
                'test', 'login-required-perms')),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

    def test_login_required_unauthenticated(self):
        response = self.client.get(
            reverse('sileo-test:api-list', args=(
                'test', 'login-required-perms')),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)


@override_settings(ROOT_URLCONF=TestUrls)
class OwnerRequiredTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(password='123')
        self.sample1 = SampleApiModel.objects.create(
            owner=self.user, title='sample', value=1.0)
        self.url = reverse('sileo-test:api-delete',
                           args=('test', 'owner-required-perms'))
        self.url += '?pk={}'.format(self.sample1.pk)

    def test_owner_required(self):
        self.client.login(
            username=self.user.username, password='123')
        response = self.client.post(
            self.url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

    def test_not_owner(self):
        self.otheruser = UserFactory(password='123')
        self.client.login(
            username=self.otheruser.username, password='123')
        response = self.client.post(
            self.url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)
