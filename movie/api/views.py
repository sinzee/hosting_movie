from rest_framework import viewsets

from ..models import (
                        SiteUser,
                     )
from . import serializers


class SiteUserListRestApiView(viewsets.ModelViewSet):
    queryset = SiteUser.objects.all()
    serializer_class = serializers.SiteUserSerializer

    def destroy(self, request, *args, **kwargs):
        user_obj = self.get_object().user
        result = super(SiteUserListRestApiView, self).destroy(request, *args, **kwargs)
        user_obj.delete()
        return result
