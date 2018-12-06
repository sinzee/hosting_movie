from rest_framework import viewsets

from ..models import (
                        Comment,
                        Movie,
                        SiteUser,
                     )
from . import serializers


class SiteUserListRestApiViewSet(viewsets.ModelViewSet):
    queryset = SiteUser.objects.all()
    serializer_class = serializers.SiteUserSerializer

    def destroy(self, request, *args, **kwargs):
        user_obj = self.get_object().user
        result = super(SiteUserListRestApiViewSet, self).destroy(request, *args, **kwargs)
        user_obj.delete()
        return result


class MovieListRestApiViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = serializers.MovieSerializer


class CommentListRestApiViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
