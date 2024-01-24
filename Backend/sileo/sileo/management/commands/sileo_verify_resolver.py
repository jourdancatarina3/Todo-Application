import collections
from collections import namedtuple

from django.core.management import BaseCommand

from sileo.fields import (
    ResourceField, ResourceGenericModel, ResourceTypeConvert,
    ResourceMethodField)
from sileo.registration import _resources, get_resource


errors_dict = {
    1: '{resource} has no field or property called "{field}"',
    2: '{resource} uses a resource that does not exist (namespace: {field.namespace}, name: {field.resource_name})',
    3: '{resource} has no method "{field}"',
    4: '{resource} fields is not a tuple.',
}


class Command(BaseCommand):
    """ Custom manange command that checks all api resources if they are valid.
    """
    help = 'Checks all api resources if they are valid'
    cache_key_stack = {}
    total_errors = 0
    total_warnings = 0

    def handle(self, *args, **kwargs):
        for namespace in _resources:
            for name in _resources[namespace]:
                resource = get_resource(namespace, name)
                self.check_resource(namespace, name, resource)
        self.write_summary()

    def check_resource(self, namespace, name, resource):
        if not isinstance(resource.fields, collections.Sequence):
            self.write_field_error(namespace, name, resource, 4)
            return

        for field in resource.fields:
            # check resolving of resource
            if isinstance(field, str):
                self.check_field(namespace, name, resource, field)
            elif isinstance(field, ResourceField):
                if isinstance(field, ResourceGenericModel):
                    for resolver in field.resolvers:
                        field_resolver = field.resolvers[resolver]
                        if isinstance(field_resolver, collections.Sequence):
                            try:
                                field_resolver = get_resource(
                                    field_resolver[0], field_resolver[1])
                            except:
                                self.write_field_error(
                                    namespace, name, resource, 2,
                                    {'namespace': field_resolver[0],
                                     'resource_name': field_resolver[1]})
                            else:
                                self.check_resource(
                                    namespace, name, field_resolver)
                elif isinstance(field, ResourceMethodField):
                    try:
                        getattr(resource, field.method_name)
                    except:
                        self.write_field_error(
                            namespace, name, resource, 3, field.method_name)
                elif isinstance(field, ResourceTypeConvert):
                    # pass because we will just check the field below
                    pass
                else:
                    try:
                        resolver_class = field.resolver_class
                    except:
                        self.write_field_error(
                            namespace, name, resource, 2, field)
                    else:
                        self.check_resource(
                            namespace, name, resolver_class)

                if not isinstance(field, ResourceMethodField):
                    self.check_field(
                        namespace, name, resource, field._property)
        self.check_cache_key(namespace, name, resource)

    def check_cache_key(self, namespace, name, resource):
        """Check if cache prefix already exists"""
        if resource.is_cached is True:
            if resource.cache_prefix not in self.cache_key_stack:
                self.cache_key_stack[resource.cache_prefix] = resource
            else:
                if resource != self.cache_key_stack[resource.cache_prefix]:
                    self.write_cache_warning(namespace, name, resource)

    def check_field(self, namespace, name, resource, field):
        """Check if model has the field. Checking order is as follows:
        1. Django Model Fields
        2. Model properties
        """
        if not (field in resource.query_set.model._meta._forward_fields_map or
                (field in dir(resource.query_set.model) and not callable(
                    getattr(resource.query_set.model, field)))):
                self.write_field_error(
                    namespace, name, resource, 1, field)

    def write_field_error(self, namespace, name, resource, error_code,
                          field=None):
        self.total_errors += 1
        if isinstance(field, dict):
            field = namedtuple('Struct', field.keys())(*field.values())

        self.stdout.write('=' * 70)
        self.stdout.write('/{}/{}'.format(namespace, name))
        self.stdout.write('Error Code: {}'.format(error_code))
        self.stdout.write(
            errors_dict[error_code].format(
                resource=resource, field=field))

    def write_cache_warning(self, namespace, name, resource):
        self.total_warnings += 1
        self.stdout.write('=' * 70)
        self.stdout.write('/{}/{}'.format(namespace, name))
        self.stdout.write('Warning')
        self.stdout.write('{} shares the same cache key with {}'.format(
            resource().__class__, self.cache_key_stack[resource.cache_prefix]))

    def write_summary(self):
        if self.total_errors == 0 and self.total_warnings == 0:
            self.stdout.write('OK')
        else:
            self.stdout.write('-' * 70)
            summary = 'FAILED (errors={}'.format(self.total_errors)
            if self.total_warnings == 0:
                summary += ')'
            else:
                summary += ', warnings={})'.format(self.total_warnings)
            self.stdout.write(self.style.ERROR(summary))
