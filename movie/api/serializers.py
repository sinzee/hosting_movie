from rest_framework import serializers

from ..models import SiteUser


class SiteUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SiteUser
        fields = ('url', 'bio', )
