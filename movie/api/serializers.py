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

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        super().update(instance, validated_data)

        if user_data:
            user_obj = instance.user

            for key, item in user_data.items():
                setattr(user_obj, key, item)
            user_obj.save()
        return instance
