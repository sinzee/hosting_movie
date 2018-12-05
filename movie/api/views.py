from rest_framework import viewsets

from ..models import (
                        SiteUser,
                     )
from . import serializers


class SiteUserListRestApiView(viewsets.ModelViewSet):
    queryset = SiteUser.objects.all()
    serializer_class = serializers.SiteUserSerializer
