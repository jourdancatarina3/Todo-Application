from collections.abc import Sequence

from .registration import get_resource
from django.conf import settings


class ResourceField(object):
    """ Base Resource field class """

    def __init__(self, prop, namespace='', resource_name='',
                 version=None, resource=None):
        """ Set properties

        Arguments:
            * prop -- the name of the model property the resource resolves
            * namespace -- the registered namespace of the resolver class
            * resource_name -- the registered name of the resolver class
            * version -- the version from which the resource belongs
            * resource -- the resolver class

        Note:
            If you provide namespace and resource_name do not provide a
            resource since the resource will be automatically determined based
            of the namespace and resource_name. Also if you provide a resource
            do not pass a namespace and resource_name since those will not be
            used.

        Sample Usage:
            ResourceField('my_field', 'namespance', 'name')
                or
            ResourceField('my_field', resource=ResourceClass)
        """
        self._property = prop
        self.resolve_resource = resource
        self.namespace = namespace
        self.resource_name = resource_name
        if version is not None:
            self.version = version
        else:
            self.version = settings.SILEO_API_FALLBACK_VERSION

    @property
    def resolver_class(self):
        if not self.resolve_resource:
            self.resolve_resource = get_resource(
                self.namespace, self.resource_name, self.version)  # noqa
        return self.resolve_resource

    def resolve(self, obj, request, **kwargs):
        """ This method needs to be implemented in the subclass

        Arguments:
            * obj -- the instance containing the property we want to resolve
            * request -- the request object
        """
        pass


class ResourceModel(ResourceField):
    """ Resource field that handles the resolving a model instance """

    def resolve(self, obj, request, **kwargs):
        instance = getattr(obj, self._property, None)
        if instance is None:
            return None
        resolver = self.resolver_class(request)
        return resolver.resolve_fields(instance)


class ResourceModelManager(ResourceField):
    """ Resource field that handles the resolving of model managers """

    def resolve(self, obj, request, **kwargs):
        manager = getattr(obj, self._property)
        resolver = self.resolver_class(request)
        result = []
        for instance in manager.all():
            result.append(resolver.resolve_fields(instance))
        return result


class ResourceQuerySet(ResourceField):
    """ Resource field that handles the resolving of queryset properties """

    def resolve(self, obj, request, **kwargs):
        queryset = getattr(obj, self._property)
        resolver = self.resolver_class(request)
        result = []
        for instance in queryset:
            result.append(resolver.resolve_fields(instance))
        return result


class ResourceGenericModel(ResourceField):
    """ Resource field that handles resolving of generic foreignkeys """

    def __init__(self, prop, resolvers):
        """ Set properties

        Arguments:
            * prop -- the name of the property that returns different types of
                      instances. usually a generic foreignkey field
            * resolvers -- a dict that specifies what resolver to use per
                      class
        Sample Usage:
            ResourceGenericModel(
                'my_field',
                {
                    'Model1': ('namespance', 'name'),
                    'Model2': ResourceForModel2
                })
        """
        self._property = prop
        self.resolvers = resolvers

    def get_resolver_class(self, instance):
        class_name = instance.__class__.__name__
        if class_name not in self.resolvers:
            return None
        resolver = self.resolvers[class_name]
        # check if the resolver is still in a namespace - name pair, not
        # a resource intance
        if isinstance(resolver, Sequence):
            resolver = get_resource(*resolver)
            self.resolvers[class_name] = resolver
        return resolver

    def resolve(self, obj, request, **kwargs):
        instance = getattr(obj, self._property)
        resolver_class = self.get_resolver_class(instance=instance)
        if resolver_class:
            resolver = resolver_class(request)
            return resolver.resolve_fields(instance)
        return None


class ResourceTypeConvert(ResourceField):
    """ Resource field that allows you to convert the type of the property you
    are trying to get

    Sample Usage:
        e.g. you have a decimal field call 'my_decimal_field'
        ResourceTypeConvert('my_decimal_field', str) to get a string
        ResourceTypeConvert('my_decimal_field', float) to get a float
    """

    def __init__(self, prop, converter):
        self._property = prop
        self.converter = converter

    def resolve(self, obj, request, **kwargs):
        value = getattr(obj, self._property, None)
        return self.converter(value) if value is not None else None


class ResourceMethodField(ResourceField):

    def __init__(self, prop, method_name=''):
        self._property = prop
        self.method_name = method_name

    def resolve(self, obj, request, resource_instance, **kwargs):
        method_name = self.method_name
        if not self.method_name:
            method_name = 'get_{prop}'.format(prop=self._property)
        method = getattr(resource_instance, method_name)
        return method(self._property, obj, request)
