from decimal import Decimal

from django.test import TestCase

from sileo.forms import field_to_dict
from sileo.tests import SampleApiModel, SampleApiModelFormWithExtraField
from sileo.tests.factories.user import UserFactory


class FormAsDictTestCase(TestCase):
    """ Test Case fir form as dict function """

    def setUp(self):
        self.user = UserFactory(password='user')
        self.sample1 = SampleApiModel.objects.create(
            owner=self.user, title='sample', value=1.0)
        self.form = SampleApiModelFormWithExtraField

    def test_as_dict(self):
        """ Test form as dict """
        form = self.form()
        data = form.as_dict()
        self.assertEqual(data['fields']['tagline']['min_length'], 5)
        self.assertEqual(data['fields']['owner'], field_to_dict(form['owner']))

    def test_as_dict_initial_type(self):
        """ Test form as dict to initial 'Decimal' type"""
        form = self.form(initial={'value': Decimal(1.0)})
        data = form.as_dict()
        self.assertEqual(data['fields']['value']['value'], float(1.0))
