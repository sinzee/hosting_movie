from django.conf.urls import include, url
from rest_framework import routers

from . import viewsets


router = routers.DefaultRouter()
router.register(r'user', viewsets.SiteUserListRestApiViewSet)
router.register(r'movie', viewsets.MovieListRestApiViewSet)

urlpatterns = [
# TODO: Do I need to set a routing at the api endpoint?
#    url(r'^$', views.index, name='index'),
    url(r'^', include(router.urls, namespace='api')),
]
