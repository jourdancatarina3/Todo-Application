from django.conf import settings
import logging
log = logging.getLogger(__name__)

_resources = {}

DEP_WARNING = "Registering %s without version falls back to 'v1'. "\
    "If inappropriate please specify version."


def register(namespace, name, resource, version=None):
    """ Register method that register a class as a resource
        api usuable in javascript
        Arguments :
            * `namespace` - resource field namespace to
                            where holds a group of resources
                            i.e. inbox(namespace) with
                            MessagesResource, ThreadResource, etc.
            * `name` - string value use to identify the
                       resource in the namespace
            * `resource` - the resource class referred and to
                           be registered as part of the api
    """

    # Check to see if the namespace exists, if not create a blank
    if not version:
        log.warning(DEP_WARNING, resource.__class__.__name__)
        version = settings.SILEO_API_FALLBACK_VERSION
    if version not in settings.SILEO_ALLOWED_VERSIONS:
        raise ValueError('Version %s not allowed ' % version)
    if version not in _resources:
        _resources[version] = {}
    resource_map = _resources.get(version)
    if namespace not in resource_map:
        resource_map[namespace] = {}
    # check to see if the name exists in the namespace
    if name in resource_map[namespace]:
        raise KeyError('Resource already registered: {0}'.format(resource))
    else:
        resource_map[namespace][name] = resource
        log.debug('Registered resource: {}'.format(resource))


def get_resource(namespace, name, version='v1'):
    """ Returns the resource
        Arguments:
            * `namespace` - the group/namespace where to look for the resource
            * `name` - the name of the resource
    """
    try:
        resource_map = _resources[version]
    except KeyError as e:
        log.debug(
            "Resource '{}':'{}' might not be available for version {}"
            .format(namespace, name, version),
            exc_info=1)
        raise e
    return resource_map[namespace][name]
