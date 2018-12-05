from django.conf.urls import include, url
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r'user', views.SiteUserListRestApiView)

urlpatterns = [
# TODO: Do I need to set a routing at the api endpoint?
#    url(r'^$', views.index, name='index'),
#    url(r'^user$', views.SiteUserListRestApiView.as_view(), name='api-user'),
    url(r'^', include(router.urls)),
]
