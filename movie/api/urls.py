from django.conf.urls import include, url
from rest_framework import routers

from . import viewsets


router = routers.DefaultRouter()
router.register(r'comment', viewsets.CommentListRestApiViewSet)
router.register(r'movie', viewsets.MovieListRestApiViewSet)
router.register(r'user', viewsets.SiteUserListRestApiViewSet)

urlpatterns = [
# TODO: Do I need to set a routing at the api endpoint?
#    url(r'^$', views.index, name='index'),
    url(r'^', include(router.urls, namespace='api')),
]
