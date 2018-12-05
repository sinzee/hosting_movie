import json
import os.path

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from movie.models import (
                             Movie,
                             SiteUser,
                         )


class RestApiTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/api/v1/user/'

        cls.mail_address = 'test@example.com'
        cls.first_name = 'Super'
        cls.last_name = 'John'
        cls.test_user = User.objects.create_user(
                            username=cls.mail_address,
                            password='12345',
                            email=cls.mail_address,
                            first_name=cls.first_name,
                            last_name=cls.last_name,
                        )
        cls.bio = 'user bio'
        cls.site_user = SiteUser.objects.create(
                            user=cls.test_user,
                            bio=cls.bio
                        )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get(self.url_path)
        self.assertEqual(resp.status_code, 200)

    def test_api_gets_user_list(self):
        resp = self.client.get(self.url_path)
        expected_data = [
                            {
                                'url': 'http://testserver{path}{pk}/'.format(
                                            path=self.url_path,
                                            pk=self.site_user.pk
                                       ),
                                'bio': self.bio,
                                'user': {
                                    'id': self.test_user.pk,
                                    'username': self.mail_address,
                                    'email': self.mail_address,
                                    'first_name': self.first_name,
                                    'last_name': self.last_name,
                                },
                            },
                        ]
        self.assertEqual(
            json.loads(resp.content),
            expected_data
        )

