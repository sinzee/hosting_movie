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
        cls.url_name = 'api-user'

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

    def setUp(self):
        self.resp = self.client.get(self.url_path)

    def test_view_url_exists_at_desired_location(self):
        self.assertEqual(self.resp.status_code, 200)


