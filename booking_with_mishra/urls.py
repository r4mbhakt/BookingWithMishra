# Shivoham Mishra | BTech

from django.contrib import admin

from django.urls import path
from django.urls import include

from users import views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path(
        'admin/',
        admin.site.urls
    ),

    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'services/',
        views.services_page,
        name='services'
    ),

    path(
        'events/',
        views.events_page,
        name='events'
    ),

    path(
        'login/',
        views.login_page,
        name='login'
    ),

    path(
        'movies/',
        include('movies.urls')
    ),
    path(
        'logout/',
        views.logout_page,
        name='logout'
    ),
]



urlpatterns += static(

    settings.MEDIA_URL,

    document_root=settings.MEDIA_ROOT
)



urlpatterns += static(

    settings.STATIC_URL,

    document_root=settings.STATIC_ROOT
)