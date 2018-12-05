from django.contrib.auth.models import User
from rest_framework import serializers

from ..models import SiteUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
                    'id',
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                 )


class SiteUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = SiteUser
        fields = (
                    'url',
                    'bio',
                    'user',
                 )
