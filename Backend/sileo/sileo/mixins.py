from django.core.cache import cache
from django.conf import settings


class LoginRequiredMixin(object):
    """ Mixin for Resources that are only accessible for logged in users """

    def has_perm(self, method, *args, **kwargs):
        has_perm = super(LoginRequiredMixin, self).has_perm(
            method, *args, **kwargs)
        if has_perm is False:
            return False
        return hasattr(self.request, 'user') and \
            self.request.user.is_authenticated()


class RateLimitMixin(object):
    """ Mixin for Resource that apply some limit on the rate of access. It uses
    cache for storing info thus it is import that the cache backend used
    supports atomic increment, decrement, and add operations (e.g. memcached)
    """

    ratelimit_methods = []
    ratelimit_rate = '1/1'          # 1 request per 1 second

    def _get_rate_limit_cache_key(self, method, *args, **kwargs):
        """ returns cache key used to store the limit data

        Arguments:
            * method -- the method name. a string signifying the method that is
                    trying to be executed. The options are filter, get_pk,
                    create, update, and delete
        """
        prefix = getattr(
            settings, 'SILEO_RATE_LIMIT_PREFIX', 'sileo_ratelimit')
        class_name = self.__class__.__name__
        key = '{}_{}_{}_{}'.format(prefix, class_name, method,
                                   self.get_rate_limit_key(
                                       method, *args, **kwargs))
        return key

    def get_rate_limit_key(self, *args, **kwargs):
        """ Returns a key that is used in the cache key. This key should make
        unrelated request that should not affect each other's limit return
        different values. By default this will return the currently logged in
        user's pk meaning requests to the resource made by the same user
        will affect the limit.
        """
        return self.request.user.pk

    def _get_rate(self):
        """ returns a tuple (number, time) representing the rate """
        return map(int, self.ratelimit_rate.split('/'))

    def _check_allowed_by_limit(self, method, *args, **kwargs):
        """ The returns False if the limit is reaced for the given method, False
        otherwise.

        Arguments:
            * method -- the method name. a string signifying the method that is
                    trying to be executed. The options are filter, get_pk,
                    create, update, and delete
        """
        if method not in self.ratelimit_methods:
            return True
        rate, per = self._get_rate()
        cache_key = self._get_rate_limit_cache_key(method, *args, **kwargs)
        was_added = cache.add(cache_key, rate, per)
        if was_added:
            return True
        try:
            val = cache.decr(cache_key)
        except ValueError:
            cache.add(cache_key, rate, per)
            val = 1
        return val > 0

    def error_data(self):
        """ Return a dict containing info that is sent in the response for
        requests that reached the limit.
        """
        return {
            'status_code': 403,
            'data': 'You have reached the rate limit!'
        }

    def dispatch(self, method, *args, **kwargs):
        if self._check_allowed_by_limit(method, *args, **kwargs) is True:
            return super(RateLimitMixin, self).dispatch(
                method, *args, **kwargs)
        return self.error_data()


class MethodLoginRequiredMixin(object):
    """ Mixin for Resources specific method that are only accessible for logged in users """
    login_required_methods = []

    def has_perm(self, method, *args, **kwargs):
        has_perm = super(MethodLoginRequiredMixin, self).has_perm(
            method, *args, **kwargs)
        if has_perm is False:
            return False
        if method in self.login_required_methods:
            return hasattr(self.request, 'user') and \
                self.request.user.is_authenticated()
        return True
