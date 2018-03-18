from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^user/(?P<pk>\d+)$', views.SiteUserDetailView.as_view(), name='user-detail'),
    url(r'^user/create$', views.SiteUserCreateView.as_view(), name='create-user'),
    url(r'^user/create/temp$', views.SiteUserCreateTemporarilyView.as_view(), name='created-user-temporarily'),
    url(r'^user/create/complete/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.SiteUserCreateCompletelyView.as_view(), name='created-user-completely'),
    url(r'^user/edit/name$', views.SiteUserUpdateNameView.as_view(), name='user-name-edit'),
    url(r'^user/edit/email$', views.SiteUserUpdateEmailView.as_view(), name='user-email-edit'),
    url(r'^user/edit/email/temp$', views.SiteUserUpdateEmailTemporarilyView.as_view(), name='user-email-edit-temporarily'),
    url(r'^user/edit/email/complete/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/(?P<new_email>[0-9A-Za-z_\-]+)$', views.SiteUserUpdateEmailCompletelyView.as_view(), name='user-email-edit-completely'),
    url(r'^user/edit/bio$', views.SiteUserUpdateBioView.as_view(), name='user-bio-edit'),
    url(r'^user/edit$', views.SiteUserUpdateIndexView.as_view(), name='user-edit-index'),
    url(r'^user/delete$', views.SiteUserDeleteView.as_view(), name='user-delete'),
    url(r'^(?P<pk>\d+)$', views.MovieDetailView.as_view(), name='movie-detail'),
    url(r'^(?P<pk>\d+)/comment$', views.MovieCommentCreateView.as_view(), name='create-comment'),
    url(r'^(?P<pk>\d+)/edit$', views.MovieUpdateView.as_view(), name='movie-edit'),
    url(r'^(?P<pk>\d+)/delete$', views.MovieDeleteView.as_view(), name='movie-delete'),
    url(r'^movies$', views.MovieListView.as_view(), name='movie-list'),
    url(r'^create$', views.MovieCreateView.as_view(), name='upload-movie'),
]
