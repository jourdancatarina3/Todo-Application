# from django.conf.urls import url
from django.urls import re_path
from .views import (
    ResourceDetailView, ResourceListView, ResourceCreateView,
    ResourceUpdateView, ResourceDeleteView, ResourceFormInfoView)

urlpatterns = (
    re_path(r'(?P<version>[\w-]+)/(?P<namespace>[\w-]+)/(?P<resource>[\w-]+)/get/(?P<pk>\d+)/$',
        ResourceDetailView.as_view(), name='api-detail-version'),
    re_path(r'(?P<namespace>[\w-]+)/(?P<resource>[\w-]+)/get/(?P<pk>\d+)/$',
        ResourceDetailView.as_view(), name='api-detail'),

    re_path(r'(?P<version>[\w-]+)/(?P<namespace>[\w-]+)/(?P<resource>[\w-]+)/filter/$',
        ResourceListView.as_view(), name='api-list-version'),
    re_path(r'(?P<namespace>[\w-]+)/(?P<resource>[\w-]+)/filter/$',
        ResourceListView.as_view(), name='api-list'),

    re_path(r'(?P<version>[\w-]+)/(?P<namespace>[\w-]+)/(?P<resource>[\w-]+)/create/$',
        ResourceCreateView.as_view(), name='api-create-version'),
    re_path(r'(?P<namespace>[\w-]+)/(?P<resource>[\w-]+)/create/$',
        ResourceCreateView.as_view(), name='api-create'),

    re_path(r'(?P<version>[\w-]+)/(?P<namespace>[\w-]+)/(?P<resource>[\w-]+)/update/$',
        ResourceUpdateView.as_view(), name='api-update-version'),
    re_path(r'(?P<namespace>[\w-]+)/(?P<resource>[\w-]+)/update/$',
        ResourceUpdateView.as_view(), name='api-update'),

    re_path(r'(?P<version>[\w-]+)/(?P<namespace>[\w-]+)/(?P<resource>[\w-]+)/delete/$',
        ResourceDeleteView.as_view(), name='api-delete-version'),
    re_path(r'(?P<namespace>[\w-]+)/(?P<resource>[\w-]+)/delete/$',
        ResourceDeleteView.as_view(), name='api-delete'),

    re_path(r'(?P<version>[\w-]+)/(?P<namespace>[\w-]+)/(?P<resource>[\w-]+)/form-info/$',
        ResourceFormInfoView.as_view(), name='api-form-info-version'),
    re_path(r'(?P<namespace>[\w-]+)/(?P<resource>[\w-]+)/form-info/$',
        ResourceFormInfoView.as_view(), name='api-form-info'),
)
