from __future__ import unicode_literals

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import Http404
from django.core.exceptions import PermissionDenied

from .fields import ResourceField


class Resource(object):
    query_set = None
    # tuple of fields will be included in the resolved dict
    fields = ()
    # tuple of filter keywords for filtering results of the filter method
    # e.g. ('pk__gt', 'title__icontains')
    filter_fields = ()
    required_filter_fields = ()
    # tuple of filter keywords for excluding results of the filter method
    exclude_filter_fields = ()

    # tuple of filter keywords for getting the instance to update in the
    # update method and form_dict method
    update_filter_fields = ()

    # tuple of filter keywords for getting the instance to deleted in the
    # delete method
    delete_filter_fields = ()

    # tuple if methods that this resource exposes
    allowed_methods = ()

    # tuple of functions that returns True or False based on the method
    method_perms = ()
    # tuple of functions that returns True or False based on the object
    object_perms = ()

    # caching options
    cache_prefix = None
    cache_timeout = None
    is_cached = False

    size_per_request = 10
    form_class = None

    def __init__(self, request=None):
        self.request = request

    def has_perm(self, method, *args, **kwargs):
        """ Method that returns True if the action is allowed and False
        otherwise

        Arguments:
            * method -- a string signifying the actions that is trying to be
                    executed. The options are filter, get_pk, create, update,
                    and delete
        """
        if method not in self.allowed_methods:
            raise Http404
        for method_perm in self.method_perms:
            if method_perm(self, method, *args, **kwargs) is False:
                return False
        return True

    def has_object_perm(self, method, obj, *args, **kwargs):
        """ Method that returns True if an action on the given object is allowed
        and False otherwise.

        Arguments:
            * method -- a string signifying the actions that is trying to be
                    executed. The options are filter, get_pk, create, update,
                    and delete
            * obj -- the model instance
        """
        for obj_perm in self.object_perms:
            if obj_perm(self, method, obj, *args, **kwargs) is False:
                return False
        return True

    def get_cache_key(self, id):
        if self.cache_prefix is not None:
            return '{}_{}'.format(self.cache_prefix, id)
        return '{}_{}'.format(self.__class__.__name__, id)

    def resolve_fields(self, obj, no_cache=False):
        """ Resolve the fields specified in the `fields` attribute and
        builds a dict

        Arguments:
            * obj -- the instance whose fields needs to be resolved
            * no_cache -- set to True if you want to bypass cache
        """
        if self.is_cached is True and no_cache is False:
            cached_response = cache.get(self.get_cache_key(obj.id))
            if cached_response is not None:
                return cached_response

        context_object = self.object_to_dict(obj=obj)

        if self.is_cached is True:
            cache.set(self.get_cache_key(obj.id), context_object,
                      self.cache_timeout)
        return context_object

    def object_to_dict(self, obj):
        """ Generate a dict containing information about the given obj based
        on the specified fields

        Arguments:
            * obj -- the instance that needs to be converted to dict
        """
        context_object = {}
        for field in self.fields:
            if issubclass(field.__class__, ResourceField):
                # resource field
                context_object[field._property] =\
                    field.resolve(
                        obj=obj, request=self.request, resource_instance=self)
            else:
                # normal field
                context_object[field] = getattr(obj, field)
        return context_object

    def _clean_filter_value(self, value):
        """ This method cleans the value passed in the kwargs """
        try:
            value = int(value)
        except ValueError:
            pass
        try:
            if value < 0:
                value = None
        except TypeError as e:
            pass
        return value

    def resolve_filters(self, filter_args, required_fields=[],
                        optional_fields=[]):
        """ Returns key-value pair for query filters. The filters will be
        based on the given lists of filter fields. Resolve appropriate value
        for none int and zero value filters.

        Arguments:
            * filter_args -- a dict of supposed to be filters for query object.
            * required_fields -- a list of required fields
            * optional_fields -- a list of optional fields
        """
        filters = {}
        if not filter_args:
            if len(required_fields) > 0:
                raise Http404
            return filters

        for field in required_fields:
            try:
                value = self._clean_filter_value(filter_args[field])
                filters[field] = value
            except KeyError:
                # raise 404 if one of the required filters is not provided
                raise Http404
        for field in optional_fields:
            if field in filter_args:
                value = self._clean_filter_value(filter_args[field])
                filters[field] = value
        return filters

    def dispatch(self, method, *args, **kwargs):
        """ This method is the entry point of the resource. The view will
        executed this method proving a method name and this method will execute
        that method described by the method name after it has determined that
        it is allowed to execute the method. The method will raise
        PermissionDenied if the action is not permitted.

        Arguments:
            method -- the method name. a string signifying the method that is
                    trying to be executed. The options are filter, get_pk,
                    create, update, and delete
            addtional parameters will be passed to the method that it is trying
            to execute.
        """
        if self.has_perm(method, *args, **kwargs) is False:
            raise PermissionDenied()
        handler = getattr(self, method)
        return handler(*args, **kwargs)

    def get_pk(self, pk):
        """ Get a record by its pk

        Arguments:
            * pk -- the pk/id of the object you want get
        """
        obj = self.get_instance(pk=pk)
        return {
            'status_code': 200,
            'data': self.resolve_fields(obj=obj)
        }

    def filter_query(self, filters, excludes, *args, **kwargs):
        """ Returns a queryset that will be used in the filter method

        Arguments:
            * filters -- a dict containing parameters for the filter query
            * excludes -- a dict containing parameters for the exclude part of
                          the query
        """
        return self.query_set.filter(**filters).exclude(**excludes)

    def filter(self, filter_args, top=0, *args, **kwargs):
        """ Return filtered query objects in list.

        Arguments:
            * filter_args -- the dict containing data for filters sent in the
                             request, this will be cleaned before passing it to
                             the filter query
            * top -- upperbound index of where to start the request.
        """

        bottom = None
        if self.size_per_request is not None:
            bottom = top + self.size_per_request
            if kwargs['bottom'] and kwargs['bottom'] < bottom:
                bottom = kwargs['bottom']
        filters = self.resolve_filters(
            filter_args, required_fields=self.required_filter_fields,
            optional_fields=self.filter_fields)
        excludes = self.resolve_filters(
            filter_args, optional_fields=self.exclude_filter_fields)
        query = self.filter_query(
            filters=filters, excludes=excludes)[top:bottom]
        objects = [self.resolve_fields(obj=obj) for obj in query]
        return {
            'status_code': 200,
            'data': objects
        }

    def get_form_class(self, *args, **kwargs):
        """ Returns the form class used for create and update methods """
        return self.form_class

    def get_form(self, *args, **kwargs):
        """ Returns the form instance using the form_class attribute of the
        resource and the arguments and keywork arguments provided in the
        parameters. This method will raise a ValueError if the resource do not
        specify a form_class.
        """
        form_class = self.get_form_class(*args, **kwargs)
        if form_class is None:
            raise ValueError('{} did not specify a form_class'.format(
                self.__class__.__name__))
        return form_class(*args, **kwargs)

    def validate_form(self, form):
        """ Returns a True if the given form is valid, False otherwise.

        Arguments:
            * form -- a rest_api form instance
        """
        return form.is_valid()

    def form_invalid(self, form):
        """ Returns a dict containing information about the errors in an invalid
        form. The dict will have a key 'status_code' which is an http status
        code and a key 'data' that contains the errors of the form.

        Arguments:
            * form -- a rest_api form instance that is invalid
        """
        return {
            'status_code': 400,
            'data': form.errors
        }

    def save(self, form, create, *args, **kwargs):
        """ Save the given form and return the instance that is the output of
        the form save process.

        Arguments:
            * form - a rest_api form instance that is already validated
            * create - a boolean that is True if the form will create a new
                     instance, False if it is just updating an existing
                     instance
            * the additional arguments will be passed to the form `save` method
        """
        instance = form.save(*args, **kwargs)
        return instance

    def create_response_data(self, obj):
        """ Returns the resolved fields dict for the given instance. This
        method is used to generate the data returned after a successful create.

        Arguments:
            * obj -- The instance that was updated
        """
        return self.resolve_fields(obj=obj)

    def create(self):
        """ Create a new record/instance using the form_class and the data
        passed throught the request object.

        Returns a dict containg a status_code that is an http status code
        and the data (dict) about the newly create record
        """
        form = self.get_form(self.request.POST, self.request.FILES)
        if self.validate_form(form=form):
            instance = self.save(form=form, create=True)
            data = self.create_response_data(obj=instance)
            return {
                'status_code': 201,
                'data': data
            }
        return self.form_invalid(form=form)

    def get_instance(self, **filters):
        """ Returns the instance given the filters parameter and the defined
        query_set of the resource. This method will raise Http404 if the object
        with the given pk does not exist or if no filter is provided.

        Arguments:
            * filters -- the keys and values used as filters
        """
        if not filters:
            raise Http404
        try:
            instance = self.query_set.get(**filters)
            self.instance = instance
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            raise Http404
        return instance

    def update_response_data(self, obj):
        """ Returns the resolved fields dict for the given instance. This
        method used to generate the data returned after a successful updated.

        Arguments:
            * obj -- The instance that was updated
        """
        return self.resolve_fields(obj=obj, no_cache=True)

    def update(self, filter_args):
        """ Update an existing record/instance references by the pk using the
        form_class and the data passed through the request object. The method
        will check first if updating the record/instance is permitted before
        performing the update. The method will raise
        PermissionDenied if the action is not permitted.

        Arguments:
            * filter_args -- the dict containing data for filters sent in the
                             request, this will be cleaned before passing it to
                             the filter query to get the instance to be updated

        Returns a dict containing a status_code that is an http status code
        and the data (dict) containing the updated information of the object
        """
        filters = self.resolve_filters(
            filter_args, required_fields=self.update_filter_fields)
        instance = self.get_instance(**filters)
        if not self.has_object_perm(method='update', obj=instance):
            raise PermissionDenied()
        return self.update_object(obj=instance)

    def update_object(self, obj):
        """ Perform update on the given object using the form.

        NOTE: you can override this method to perform updates without using a
        form class but please do not abuse. Using forms is still the ideal way.

        Arguments:
            obj -- the instance to be updated

        Return:
            a dictionary containing the data and the status_code
        """
        form = self.get_form(
            self.request.POST, self.request.FILES, instance=obj)
        if self.validate_form(form=form):
            instance = self.save(form=form, create=False)
            data = self.update_response_data(obj=instance)
            return {
                'status_code': 200,
                'data': data
            }
        return self.form_invalid(form=form)

    def delete(self, filter_args):
        """ Delete/remove a record/instance that is referenced by the given
        filter. The method will check first if deleting/removing the instance
        is permitted before deleting the record. The method will raise
        PermissionDenied if the action is not permitted.

        Arguments:
            filter_args - the dict containing data for filters sent in the
                          request, this will be cleaned before passing it to
                          the filter query to get the instance to be deleted
        """
        filters = self.resolve_filters(
            filter_args, required_fields=self.delete_filter_fields)
        instance = self.get_instance(**filters)
        if not self.has_object_perm(method='delete', obj=instance):
            raise PermissionDenied()
        return {
            'status_code': 200,
            'data': self.delete_object(obj=instance)
        }

    def delete_object(self, obj):
        """ Mark an object as deleted.

        Arguments:
            * obj - the instance that needs to be deleted
        """
        obj.removed = True
        obj.save(update_fields=['removed'])
        return {'pk': obj.pk}

    def form_to_dict(self, form):
        """ Returns a dict representing the given form. The dict contains
        information about the form including its fields.

        Arguments:
            form - a rest_api.forms.Form instance
        """
        form_dict = form.as_dict()
        return form_dict

    def form_dict(self, filter_args):
        """ Returns a dict that represents form form_class of the resource.

        Arguments:
            * filter_args - an optional dict containing data for filters sent
                in the request, this will be cleaned before passing it to the
                filter query to get the instance that the form is trying to
                edit. Provide this argument to have the initial value of the
                form prepopulated using the info af an existing instance.
        """
        form_kwargs = {}
        if filter_args:
            filters = self.resolve_filters(
                filter_args, required_fields=self.update_filter_fields)
            instance = self.get_instance(**filters)
            if not self.has_object_perm(method='form_dict', obj=instance):
                raise PermissionDenied()
            form_kwargs['instance'] = instance
        form = self.get_form(**form_kwargs)
        return {
            'status_code': 200,
            'data': self.form_to_dict(form=form)
        }
