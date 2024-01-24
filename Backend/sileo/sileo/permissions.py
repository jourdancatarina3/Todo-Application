def login_required(resource, *args, **kwargs):
    """ permission method that returns True is the user is authenticated, False
    otherwise

    Arguments:
        resource -- the Resource intance that is calling this method
    """
    request = resource.request
    return hasattr(request, 'user') and request.user.is_authenticated


def owner_required(resource, method, obj, *args, **kwargs):
    """ permission method that returns True if the objects is owned by
    the currently logged in user.

    Arguments:
        resource -- the Resource instance that is calling this method
        obj -- the object that you want to operate on
        method -- a string signifying the actions that is trying to be
                    executed. The options are filter, get_pk, create, update,
                    and delete
    """
    user = resource.request.user
    return obj.owner_id == user.id
