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

        mail_address = 'test@example.com'
        test_user = User.objects.create_user(
                        username=mail_address,
                        password='12345',
                        email=mail_address,
                        first_name='Super',
                        last_name='John',
                    )
        cls.site_user = SiteUser.objects.create(
                            user=test_user,
                            bio='user bio'
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
                                'bio': 'user bio',
                            },
                        ]
        self.assertEqual(
            json.loads(resp.content),
            expected_data
        )

    def test_api_gets_user_detail(self):
        resp = self.client.get(
                '{path}{pk}/'.format(
                    path=self.url_path,
                    pk=self.site_user.pk
                )
               )
        expected_data = {
                            'url': 'http://testserver{path}{pk}/'.format(
                                        path=self.url_path,
                                        pk=self.site_user.pk
                                   ),
                            'bio': 'user bio',
                        }
        self.assertEqual(
            json.loads(resp.content),
            expected_data
        )


