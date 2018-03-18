from unittest import mock

from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.storage import get_storage_class
from django.test import TestCase

from ..models import (
                        Comment,
                        Movie,
                        SiteUser,
                     )


class SiteUserModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.site_user_url = '/movie/user/{user_id}'

        mail_address = 'test@example.com'
        test_user1 = User.objects.create_user(
                         username=mail_address,
                         password='12345',
                         email=mail_address,
                         first_name='Super',
                         last_name='John'
                     )
        cls.site_user1 = SiteUser.objects.create(user=test_user1, bio='This is a bio')

    def setUp(self):
        self.site_user = SiteUser.objects.get(id=str(self.site_user1.id))

    def test_get_absolute_url(self):
        self.assertEqual(
            self.site_user.get_absolute_url(),
            self.site_user_url.format(user_id=str(self.site_user1.id))
        )

    def test_user_label(self):
        field_label = self.site_user._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_bio_label(self):
        field_label = self.site_user._meta.get_field('bio').verbose_name
        self.assertEqual(field_label, 'bio')

    def test_bio_max_length(self):
        max_length = self.site_user._meta.get_field('bio').max_length
        self.assertEqual(max_length, 1000)

    def test_object_name(self):
        expected_object_name = '{first_name} {last_name}'.format(
                                   first_name=self.site_user.user.first_name,
                                   last_name=self.site_user.user.last_name
                               )
        self.assertEqual(expected_object_name, str(self.site_user))


class MovieModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.movie_url = '/movie/{movie_id}'

        mail_address = 'test@example.com'
        test_user1 = User.objects.create_user(
                         username=mail_address,
                         password='12345',
                         email=mail_address,
                         first_name='Super',
                         last_name='John'
                     )
        uploader1 = SiteUser.objects.create(user=test_user1, bio='This is a bio')
        movie_name1 = 'movie title'
        description1 = 'movie desc'
        upload_file1 = mock.MagicMock(spec=File, name='FileMock')
        upload_file1.name = 'test_file1.mp4'

        cls.movie1 = Movie.objects.create(
            uploaded_file=upload_file1,
            uploader=uploader1,
            movie_name=movie_name1,
            description=description1
        )

    def setUp(self):
        self.movie = Movie.objects.get(id=str(self.movie1.id))

    def test_get_absolute_url(self):
        self.assertEqual(
            self.movie.get_absolute_url(),
            self.movie_url.format(
                movie_id=str(self.movie.id)
            )
        )

    def test_uploader_label(self):
        field_name = self.movie._meta.get_field('uploader').verbose_name
        self.assertEqual(field_name, 'uploader')

    def test_movie_name_label(self):
        field_name = self.movie._meta.get_field('movie_name').verbose_name
        self.assertEqual(field_name, 'movie name')

    def test_description_label(self):
        field_name = self.movie._meta.get_field('description').verbose_name
        self.assertEqual(field_name, 'description')

    def test_upload_file_label(self):
        field_name = self.movie._meta.get_field('uploaded_file').verbose_name
        self.assertEqual(field_name, 'uploaded file')

    def test_movie_name_max_length(self):
        max_length = self.movie._meta.get_field('movie_name').max_length
        self.assertEqual(max_length, 100)

    def test_decription_max_length(self):
        max_length = self.movie._meta.get_field('description').max_length
        self.assertEqual(max_length, 1000)

    def test_object_name(self):
        self.assertEqual(str(self.movie), self.movie.movie_name)

    def test_remove_file_after_removing_object(self):
        storage = self.movie.uploaded_file.storage
        self.movie.delete()
        self.assertFalse(storage.exists(self.movie.uploaded_file.path))

# TODO: add ordering test


class CommentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # cls.movie_url = '/movie/{movie_id}'

        mail_address1 = 'test1@example.com'
        test_user1 = User.objects.create_user(
                         username=mail_address1,
                         password='12345',
                         email=mail_address1,
                         first_name='Super',
                         last_name='John'
                     )
        uploader1 = SiteUser.objects.create(user=test_user1, bio='This is a bio')

        mail_address2 = 'test2@example.com'
        test_user2 = User.objects.create_user(
                         username=mail_address2,
                         password='12345',
                         email=mail_address2,
                         first_name='Super',
                         last_name='Bob'
                     )
        cls.commenter1 = SiteUser.objects.create(user=test_user2, bio='This is a bio')

        movie_name1 = 'movie title'
        description1 = 'movie desc'
        upload_file1 = mock.MagicMock(spec=File, name='FileMock')
        upload_file1.name = 'test_file1.mp4'
        movie1 = Movie.objects.create(
            uploaded_file=upload_file1,
            uploader=uploader1,
            movie_name=movie_name1,
            description=description1
        )
        cls.movie1 = Movie.objects.get(id=str(movie1.id))

    def setUp(self):
        self.comment1 = Comment.objects.create(
                            movie=self.movie1,
                            commenter=self.commenter1,
                            description='comment desc',
                        )
        self.comment2 = Comment.objects.create(
                            movie=self.movie1,
                            commenter=self.commenter1,
                            description='0123456789'\
                                        '0123456789'\
                                        '0123456789'\
                                        '0123456789'\
                                        '0123456789'\
                                        '0123456789'\
                                        '0123456789'\
                                        '0123456789'\
                        )

    def test_commenter_label(self):
        field_name = self.comment1._meta.get_field('commenter').verbose_name
        self.assertEqual(field_name, 'commenter')

    def test_movie_label(self):
        field_name = self.comment1._meta.get_field('movie').verbose_name
        self.assertEqual(field_name, 'movie')

    def test_description_label(self):
        field_name = self.comment1._meta.get_field('description').verbose_name
        self.assertEqual(field_name, 'description')

    def test_post_date_label(self):
        field_name = self.comment1._meta.get_field('post_date').verbose_name
        self.assertEqual(field_name, 'post date')

    def test_comment_max_length(self):
        max_length = self.comment1._meta.get_field('description').max_length
        self.assertEqual(max_length, 250)

    def test_comment_max_length(self):
        max_length = self.comment1._meta.get_field('description').max_length
        self.assertEqual(max_length, 250)

    def test_object_name(self):
        self.assertEqual(str(self.comment1), self.comment1.description)

    def test_object_name_when_comment_description_is_over_75_characters(self):
        self.assertEqual(
            str(self.comment2),
            self.comment2.description[:75]
        )
