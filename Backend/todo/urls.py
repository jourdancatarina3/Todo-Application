from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-sileo/', include(('sileo.sileo.urls', 'sileo'), namespace='sileo'))
]
