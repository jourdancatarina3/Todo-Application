from __future__ import unicode_literals

import factory

from django.contrib.auth.models import User
from django.utils import timezone

__all__ = (
    'UserFactory',
)


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'test-user-%s' % n)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password')

    is_active = True
    is_staff = False
    is_superuser = False

    last_login = factory.LazyFunction(timezone.now)
    date_joined = factory.LazyAttribute(
        lambda o: o.last_login - timezone.timedelta(days=1))

    class Params:
        superuser = factory.Trait(
            is_staff=True,
            is_superuser=True
        )
