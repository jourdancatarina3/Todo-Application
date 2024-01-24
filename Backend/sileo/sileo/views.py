import json

from django.http import Http404, HttpResponse
from django.conf import settings
from django.utils.module_loading import import_string
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied

from . import registration


class BaseResourceView(View):
    """The base Resource view. The various types of Resource views are derived
    from here.
    """

    def resolve_resource(self, **kwargs):
        """Set resource as a property of the view."""
        version = kwargs.get('version', settings.SILEO_API_FALLBACK_VERSION)
        namespace = kwargs['namespace']
        resource_name = kwargs['resource']
        try:
            self.resource = registration.get_resource(
                namespace, resource_name, version)(self.request)
        except KeyError:
            raise Http404

    def process_pre_resolve(self, **kwargs):
        """Run the api middleware before the view resolves api data."""
        api_kwargs = kwargs.copy()
        if 'version' not in kwargs:
            api_kwargs['version'] = settings.SILEO_API_FALLBACK_VERSION
        for api_mid in settings.API_MIDDLEWARE:
            api_mid = import_string(api_mid)()

            api_mid.pre_api_resolve(**api_kwargs)

    def process_post_resolve(self, **kwargs):
        """Run the api middleware after the view resolves api data."""
        for api_mid in settings.API_MIDDLEWARE:
            api_mid = import_string(api_mid)()
            api_mid.post_api_resolve()

    def get_response_from_context(self, context):
        """ Return a HttpResponse object from the given context. The status
        code will be based on the `status_code` key from the context
        """
        status_code = context.pop('status_code', 200)
        data = context.pop('data', None)
        if data is None:
            data = context
        context = {'data': data}
        return HttpResponse(json.dumps(context), status=status_code,
                            content_type='application/json')


class SafeResourceView(BaseResourceView):
    """ Base method that all Resource view for safe methods are derived from.
    """

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs)
        return self.get_response_from_context(context=context)

    def get_context_data(self, **kwargs):
        """Call resolve resource when this function is invoked."""
        self.resolve_resource(**kwargs)
        return {}


class ResourceDetailView(SafeResourceView):
    """ A Resource view to show a single record by it's pk """
    def get_context_data(self, **kwargs):
        """Get and return context data containing the resolved api resource."""
        context = super(ResourceDetailView, self).get_context_data(**kwargs)

        kwargs['method_name'] = 'get_pk'
        self.process_pre_resolve(**kwargs)
        pk = int(kwargs['pk'])
        try:
            context = self.resource.dispatch(method='get_pk', pk=pk)
        except PermissionDenied:
            self.process_post_resolve(**kwargs)
            raise
        self.process_post_resolve(**kwargs)
        return context


class ResourceListView(SafeResourceView):
    """ A resource view to show a list of records that matches a given
    filter.
    """
    def get_context_data(self, **kwargs):
        """Get and return context data containing the resolved api resource."""
        context = super(ResourceListView, self).get_context_data(**kwargs)

        kwargs['method_name'] = 'filter'
        self.process_pre_resolve(**kwargs)

        request_dict = self.request.GET.dict()
        top, bottom = (0, None)
        if 'top' in request_dict:
            top = int(request_dict.pop('top'))
        if 'bottom' in request_dict:
            b = int(request_dict.pop('bottom'))
            # django queryset does not support negative indexing
            if b >= 0:
                bottom = b
        try:
            context = self.resource.dispatch(
                method='filter', filter_args=request_dict, top=top,
                bottom=bottom)
        except PermissionDenied:
            self.process_post_resolve(**kwargs)
            raise

        self.process_post_resolve(**kwargs)
        return context


class ResourceFormInfoView(SafeResourceView):
    """ A resource view to show info containing the information about the
    resource's form.
    """
    def get_context_data(self, **kwargs):
        context = super(ResourceFormInfoView, self).get_context_data(**kwargs)

        kwargs['method_name'] = 'form_dict'
        self.process_pre_resolve(**kwargs)

        request_dict = self.request.GET.dict()
        try:
            context = self.resource.dispatch(
                method='form_dict', filter_args=request_dict)
        except PermissionDenied:
            self.process_post_resolve(**kwargs)
            raise

        self.process_post_resolve(**kwargs)
        return context


class UnsafeResourceView(BaseResourceView):
    """ Base method that all Resource view for unsafe methods are
    derived from.
    """

    # @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UnsafeResourceView, self).dispatch(
            request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs)
        return self.get_response_from_context(context=context)

    def get_context_data(self, *args, **kwargs):
        self.resolve_resource(**kwargs)
        return {}


class ResourceCreateView(UnsafeResourceView):
    """ Resource view for creating a new instance using a Resource """

    def get_context_data(self, *args, **kwargs):
        super(ResourceCreateView, self).get_context_data(**kwargs)

        kwargs['method_name'] = 'create'
        self.process_pre_resolve(**kwargs)
        try:
            context = self.resource.dispatch(method='create')
        except PermissionDenied:
            self.process_post_resolve(**kwargs)
            raise
        self.process_post_resolve(**kwargs)
        return context


class ResourceUpdateView(UnsafeResourceView):
    """ Resource view for editing an existing instance given a pk """

    def get_context_data(self, *args, **kwargs):
        super(ResourceUpdateView, self).get_context_data(**kwargs)

        kwargs['method_name'] = 'update'
        self.process_pre_resolve(**kwargs)
        request_dict = self.request.GET.dict()
        try:
            context = self.resource.dispatch(
                method='update', filter_args=request_dict)
        except PermissionDenied:
            self.process_post_resolve(**kwargs)
            raise
        self.process_post_resolve(**kwargs)
        return context


class ResourceDeleteView(UnsafeResourceView):
    """ Resource view for deleting an instance givn a pk """

    def get_context_data(self, *args, **kwargs):
        super(ResourceDeleteView, self).get_context_data(**kwargs)

        kwargs['method_name'] = 'delete'
        self.process_pre_resolve(**kwargs)
        request_dict = self.request.GET.dict()
        try:
            context = self.resource.dispatch(
                method='delete', filter_args=request_dict)
        except PermissionDenied:
            self.process_post_resolve(**kwargs)
            raise
        self.process_post_resolve(**kwargs)
        return context
