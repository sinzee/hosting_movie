from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms
from django.test import TestCase

from movie.forms import (
                            MovieUploadForm,
                            SiteUserCreateForm,
                            SiteUserUpdateEmailForm,
                        )


class MovieUploadFormTest(TestCase):

    def test_uploaded_files_have_valid_extention(self):
        not_file_data = {
                            'movie_name': 'movie name',
                            'description': 'movie desc',
                        }

        mp4_ext_file = SimpleUploadedFile('test_movie.mp4', b'\x00\x00\x00 ftypisom\x00\x00\x02\x00')
        file_data1 = {
                        'uploaded_file': mp4_ext_file,
                     }
        form1 = MovieUploadForm(not_file_data, file_data1)
        self.assertTrue(form1.is_valid())

        mp3_ext_file = SimpleUploadedFile('test_movie.mp3', b'\x00\x00\x00 ftypisom\x00\x00\x02\x00')
        file_data2 = {
                        'uploaded_file': mp3_ext_file,
                     }
        form2 = MovieUploadForm(not_file_data, file_data2)
        self.assertFalse(form2.is_valid())

    def test_uploaded_files_hava_valid_magic_number(self):
        not_file_data = {
                            'movie_name': 'movie name',
                            'description': 'movie desc',
                        }

        mp4_number_file = SimpleUploadedFile('test_movie.mp4', b'\x00\x00\x00 ftypisom\x00\x00\x02\x00')
        file_data1 = {
                        'uploaded_file': mp4_number_file,
                     }
        form1 = MovieUploadForm(not_file_data, file_data1)
        self.assertTrue(form1.is_valid())

        mp3_number_file = SimpleUploadedFile('test_movie.mp4', b'\x49\x44\x33')
        file_data2 = {
                        'uploaded_file': mp3_number_file,
                     }
        form2 = MovieUploadForm(not_file_data, file_data2)
        self.assertFalse(form2.is_valid())


class SiteUserCreateFormTest(TestCase):

    def test_creating_user(self):
        mail_address = 'test@example.com'
        password = '12345'
        user = {
                    'email': mail_address,
                    'password': password,
                    'confirm_password': password,
                    'first_name': 'first1',
                    'last_name': 'last1',
               }
        form = SiteUserCreateForm(user)
        self.assertTrue(form.is_valid())

    def test_creating_user_already_exists(self):
        mail_address = 'test@example.com'
        user1 = {
                    'email': mail_address,
                    'password': 'password1',
                    'first_name': 'first1',
                    'last_name': 'last1',
                }
        User.objects.create_user(
            username=mail_address,
            **user1
        )

        password = '12345'
        user2 = {
                    'email': mail_address,
                    'password': password,
                    'confirm_password': password,
                    'first_name': 'first2',
                    'last_name': 'last2',
                }
        form = SiteUserCreateForm(user2)
        self.assertFalse(form.is_valid())

    def test_raise_error_if_first_name_have_no_value(self):
        password = '12345'
        user = {
                    'email': 'test@example.com',
                    'password': password,
                    'confirm_password': password,
                    'first_name': '',
                    'last_name': 'last1',
               }
        form = SiteUserCreateForm(user)
        self.assertFalse(form.is_valid())

    def test_raise_error_if_last_name_have_no_value(self):
        password = '12345'
        user = {
                    'email': 'test@example.com',
                    'password': password,
                    'confirm_password': password,
                    'first_name': 'first1',
                    'last_name': '',
               }
        form = SiteUserCreateForm(user)
        self.assertFalse(form.is_valid())

    def test_raise_error_if_email_have_no_value(self):
        password = '12345'
        user = {
                    'email': '',
                    'password': password,
                    'confirm_password': password,
                    'first_name': 'first1',
                    'last_name': 'last1',
               }
        form = SiteUserCreateForm(user)
        self.assertFalse(form.is_valid())

    def test_raise_error_if_password_have_no_value(self):
        password = '12345'
        user = {
                    'email': 'test@example.com',
                    'password': '',
                    'confirm_password': password,
                    'first_name': 'first1',
                    'last_name': 'last1',
               }
        form = SiteUserCreateForm(user)
        self.assertFalse(form.is_valid())

    def test_raise_error_if_confirm_password_have_no_value(self):
        password = '12345'
        user = {
                    'email': 'test@example.com',
                    'password': password,
                    'confirm_password': '',
                    'first_name': 'first1',
                    'last_name': 'last1',
               }
        form = SiteUserCreateForm(user)
        self.assertFalse(form.is_valid())

    def test_raise_error_if_password_dont_match_with_confirm_password(self):
        user = {
                    'email': 'test@example.com',
                    'password': '12345',
                    'confirm_password': '67890',
                    'first_name': 'first1',
                    'last_name': 'last1',
               }
        form = SiteUserCreateForm(user)
        self.assertFalse(form.is_valid())

    def test_password_input_is_not_visible(self):
        form = SiteUserCreateForm()
        self.assertEqual(type(form.fields['password'].widget), type(forms.PasswordInput()))

    def test_confirm_password_input_is_not_visible(self):
        form = SiteUserCreateForm()
        self.assertEqual(type(form.fields['confirm_password'].widget), type(forms.PasswordInput()))


class SiteUserUpdateEmailFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.email = 'test@example.com'
        User.objects.create_user(
            username=cls.email,
            password='12345',
            email=cls.email,
            first_name='first',
            last_name='last'
        )

    def test_raise_error_when_email_address_has_already_existed(self):
        form = SiteUserUpdateEmailForm(data={'email': self.email, })
        self.assertFalse(form.is_valid())
