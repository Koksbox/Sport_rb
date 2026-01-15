from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('auth/', include('apps.authn.api.urls')),
        path('users/', include('apps.users.api.urls')),
        path('organizations/', include('apps.organizations.api.urls')),
        path('athletes/', include('apps.athletes.api.urls')),
        path('coaches/', include('apps.coaches.api.urls')),
        path('training/', include('apps.training.api.urls')),
        path('events/', include('apps.events.api.urls')),
        path('city-committee/', include('apps.city_committee.api.urls')),
        path('analytics/', include('apps.analytics.api.urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
