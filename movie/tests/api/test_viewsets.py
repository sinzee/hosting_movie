import json
import os.path
from unittest import mock 

from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from movie.models import (
                             Comment,
                             Movie,
                             SiteUser,
                         )


class RestApiSiteUserTest(TestCase):

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

    def test_api_updates_user_bio(self):
        new_bio = 'new bio'
        update_data = json.dumps(
                        {
                          'bio': new_bio,
                        }
                      )
        resp = self.client.patch(
                '{path}{pk}/'.format(
                    path=self.url_path,
                    pk=str(self.site_user.pk)
                ),
                content_type='application/json',
                data=update_data
               )
        self.assertEqual(resp.status_code, 200)
        site_user = SiteUser.objects.get(pk=self.site_user.pk)
        self.assertEqual(site_user.bio, new_bio)

    def test_api_update_user_first_name(self):
        new_first_name = 'new_first'
        update_data = json.dumps(
                        {
                            'user': {
                                'first_name': new_first_name,
                            },
                        }
                      )
        resp = self.client.patch(
                '{path}{pk}/'.format(
                    path=self.url_path,
                    pk=str(self.site_user.pk)
                ),
                content_type='application/json',
                data=update_data
               )
        self.assertEqual(resp.status_code, 200)
        user = User.objects.get(pk=self.site_user.user.pk)
        self.assertEqual(user.first_name, new_first_name)

    def test_api_update_user_first_name(self):
        new_mail_address = 'new@example.com'
        update_data = json.dumps(
                        {
                            'user': {
                                'email': new_mail_address,
                            },
                        }
                      )
        resp = self.client.patch(
                '{path}{pk}/'.format(
                    path=self.url_path,
                    pk=str(self.site_user.pk)
                ),
                content_type='application/json',
                data=update_data
               )
        self.assertEqual(resp.status_code, 200)
        user = User.objects.get(pk=self.site_user.user.pk)
        self.assertEqual(user.email, new_mail_address)
        self.assertEqual(user.username, new_mail_address)

    def test_api_create_user(self):
        bio = 'user bio'
        email = 'user1@example.com'
        first_name = 'user1_first'
        last_name = 'user1_last'
        password = 'user1_pass'
        user_info = {
            'bio': bio,
            'user': {
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'password': password,
            },
        }
        resp = self.client.post(
                self.url_path,
                content_type='application/json',
                data=json.dumps(user_info)
               )
        self.assertEqual(resp.status_code, 201)
        user_id = json.loads(resp.content)['user']['id']
        user_obj = User.objects.get(id=user_id)
        self.assertEqual(user_obj.email, email)
        self.assertEqual(user_obj.first_name, first_name)
        self.assertEqual(user_obj.last_name, last_name)
        self.assertEqual(user_obj.username, email)
        self.assertNotEqual(user_obj.password, password)
        siteuser_obj = SiteUser.objects.get(user=user_obj)
        self.assertEqual(siteuser_obj.bio, bio)

    def test_api_delete_user(self):
        resp = self.client.delete(
                '{path}{pk}/'.format(
                    path=self.url_path,
                    pk=self.site_user.pk
                )
               )
        self.assertEqual(resp.status_code, 204)
        user_obj = User.objects.filter(pk=self.test_user.pk)
        self.assertFalse(user_obj.exists())

class RestApiMovieTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/api/v1/movie/'

        mail_address = 'test@example.com'
        test_user = User.objects.create_user(
                        username=mail_address,
                        password='12345',
                        email=mail_address,
                        first_name='test_first',
                        last_name='test_last',
                    )
        cls.site_user = SiteUser.objects.create(
                            user=test_user,
                            bio='user bio'
                        )
        cls.movie_name = 'movie_name'
        cls.description = 'movie_desc'
        upload_file = mock.MagicMock(spec=File, name='FileMock')
        upload_file.name = 'file_name.mp4'
        cls.movie = Movie.objects.create(
                        uploader=cls.site_user,
                        movie_name=cls.movie_name,
                        description=cls.description,
                        uploaded_file=upload_file
                    )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get(self.url_path)
        self.assertEqual(resp.status_code, 200)

    def test_get_correct_data_via_rest_api(self):
        resp = self.client.get(self.url_path)
        resp_data = json.loads(resp.content)
        expected_data = [
            {
                'url': 'http://testserver{path}{pk}/'.format(
                    path=self.url_path,
                    pk=self.movie.pk
                ),
                'uploader': self.site_user.pk,
                'movie_name': self.movie_name,
                'description': self.description,
                'uploaded_file': resp_data[0]['uploaded_file']
            },
        ]
        self.assertEqual(
            resp_data,
            expected_data
        )

    def test_update_movie_info_via_rest_api(self):
        new_movie_name = 'new title'
        new_data = json.dumps(
            {
                'movie_name': new_movie_name,
            }
        )
        resp = self.client.patch(
                '{path}{pk}/'.format(
                    path=self.url_path,
                    pk=self.movie.pk
                ),
                content_type='application/json',
                data=new_data
               )
        self.assertEqual(resp.status_code, 200)
        movie_obj = Movie.objects.get(pk=self.movie.pk)
        self.assertEqual(movie_obj.movie_name, new_movie_name)

    def test_delete_movie_via_rest_api(self):
        resp = self.client.delete(
                '{path}{pk}/'.format(
                    path=self.url_path,
                    pk=self.movie.pk
                )
               )
        self.assertEqual(resp.status_code, 204)
        movie_obj = Movie.objects.filter(pk=self.movie.pk)
        self.assertFalse(movie_obj.exists())

    def test_create_movie_via_rest_api(self):
        movie_name = 'movie title'
        description = 'movie desc'
        mp4_number_file = SimpleUploadedFile('test_movie.mp4', b'\x00\x00\x00 ftypisom\x00\x00\x02\x00')
        upload_data = {
            'uploader': self.site_user.pk,
            'movie_name': movie_name,
            'description': description,
            'uploaded_file': mp4_number_file,
        }
        resp = self.client.post(
                self.url_path,
                data=upload_data,
                format='multipart'
               )
        self.assertEqual(resp.status_code, 201)
        movie_id = int(json.loads(resp.content)['url'].split(
                        self.url_path
                    )[1].rstrip('/')
                   )
        movie_obj = Movie.objects.get(pk=movie_id)
        self.assertNotEqual(len(movie_obj.uploaded_file.path), 0)

class RestApiCommentTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/api/v1/comment/'

        mail_address = 'test@example.com'
        test_user = User.objects.create_user(
                        username=mail_address,
                        password='12345',
                        email=mail_address,
                        first_name='test_first',
                        last_name='test_last',
                    )
        cls.site_user = SiteUser.objects.create(
                            user=test_user,
                            bio='user bio'
                        )
        movie_name = 'movie_name'
        description = 'movie_desc'
        upload_file = mock.MagicMock(spec=File, name='FileMock')
        upload_file.name = 'file_name.mp4'
        cls.movie = Movie.objects.create(
                        uploader=cls.site_user,
                        movie_name=movie_name,
                        description=description,
                        uploaded_file=upload_file
                    )
        cls.comment_desc = 'comment content'
        cls.comment = Comment.objects.create(
                        movie=cls.movie,
                        commenter=cls.site_user,
                        description=cls.comment_desc
                      )

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get(self.url_path)
        self.assertEqual(resp.status_code, 200)

    def test_get_correct_data_via_rest_api(self):
        resp = self.client.get(self.url_path)
        resp_data = json.loads(resp.content)
        expected_data = [
            {
                'url': 'http://testserver{path}{pk}/'.format(
                    path=self.url_path,
                    pk=self.comment.pk
                ),
                'commenter': self.site_user.pk,
                'movie': self.movie.pk,
                'description': self.comment_desc,
            },
        ]
        self.assertEqual(
            resp_data,
            expected_data
        )

    def test_create_comment_via_rest_api(self):
        new_data = {
            'commenter': self.site_user.pk,
            'movie': self.movie.pk,
            'description': 'new_comment',
        }
        resp = self.client.post(
                self.url_path,
                content_type='application/json',
                data=json.dumps(
                    new_data
                )
               )
        self.assertEqual(resp.status_code, 201)
        comment_id = int(
                        json.loads(resp.content)['url'].split(self.url_path)[1].rstrip('/')
                     )
        comment_obj = Comment.objects.get(pk=comment_id)
        self.assertEqual(new_data['commenter'], comment_obj.commenter.pk)
        self.assertEqual(new_data['movie'], comment_obj.movie.pk)
        self.assertEqual(new_data['description'], comment_obj.description)

    def test_update_comment_via_rest_api(self):
        new_comment = 'new comment'
        new_data = { 'description': new_comment, }
        resp = self.client.patch(
                '{path}{pk}/'.format(
                    path=self.url_path,
                    pk=self.comment.pk
                ),
                content_type='application/json',
                data=json.dumps(new_data)
               )
        self.assertEqual(resp.status_code, 200)
        comment_obj = Comment.objects.get(pk=self.comment.pk)
        self.assertEqual(comment_obj.description, new_comment)

    def test_delete_comment_via_rest_api(self):
        comment_pk = self.comment.pk
        resp = self.client.delete(
                '{path}{pk}/'.format(
                    path=self.url_path,
                    pk=comment_pk
                )
               )
        self.assertEqual(resp.status_code, 204)
        comment_obj = Comment.objects.filter(pk=comment_pk)
        self.assertFalse(comment_obj.exists())
        

class RestApiSiteUserTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/api/v1/user/'

        cls.normal_mail_address = 'test@example.com'
        cls.normal_password = 'password'
        cls.normal_user = User.objects.create_user(
                              username=cls.normal_mail_address,
                              password=cls.normal_password,
                              email=cls.normal_mail_address,
                              first_name='norm_first',
                              last_name='norm_last',
                          )
        cls.bio = 'user bio'
        cls.site_user = SiteUser.objects.create(
                            user=cls.normal_user,
                            bio=cls.bio
                        )
        cls.admin_mail_address = 'admin@example.com'
        cls.admin_password = 'password'
        cls.admin_user = User.objects.create_user(
                            username=cls.admin_mail_address,
                            password=cls.admin_password,
                            email=cls.admin_mail_address,
                            first_name='adm_first',
                            last_name='adm_last',
                            is_staff=True
                         )

    def test_not_having_logined_user_cannot_get_data_via_rest_api(self):
        resp = self.client.get(self.url_path)
        self.assertEqual(resp.status_code, 403)

    def test_not_admin_user_cannot_get_data_via_rest_api(self):
        self.client.login(username=self.normal_mail_address, password=self.normal_password)
        resp = self.client.get(self.url_path)
        self.assertEqual(resp.status_code, 403)

    def test_admin_user_can_get_data_via_rest_api(self):
        self.client.login(username=self.admin_mail_address, password=self.admin_password)
        resp = self.client.get(self.url_path)
        self.assertEqual(resp.status_code, 200)

