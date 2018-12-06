from django.contrib.auth.models import User
from rest_framework import serializers

from ..models import (
                        SiteUser,
                        Movie,
                     )


class UserSerializer(serializers.ModelSerializer):


    class Meta:
        model = User
        fields = (
                    'id',
                    'email',
                    'first_name',
                    'last_name',
                 )


class SiteUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    url = serializers.HyperlinkedIdentityField(
            view_name='api:siteuser-detail'
          )


    class Meta:
        model = SiteUser
        fields = (
                    'url',
                    'bio',
                    'user',
                 )

    def create(self, validated_data):
        user_data = validated_data.pop('user', None)
        user_data['username'] = user_data['email']
        user_obj = User.objects.create_user(**user_data)
        validated_data['user'] = user_obj
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        super().update(instance, validated_data)

        if user_data:
            user_obj = instance.user

            for key, item in user_data.items():
                setattr(user_obj, key, item)

                if key == 'email':
                    setattr(user_obj, 'username', item)
            user_obj.save()
        return instance


class MovieSerializer(serializers.ModelSerializer):


    class Meta:
        model = Movie
        fields = (
                    'url',
                    'uploader',
                    'movie_name',
                    'description',
                 )
