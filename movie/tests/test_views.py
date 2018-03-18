import os.path
from time import sleep
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.core.files import File
from django.core.files.base import ContentFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from movie.models import (
                             Movie,
                             SiteUser,
                         )


class IndexViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/movie/'
        cls.url_name = 'index'

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get(self.url_path)
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse(self.url_name))
        self.assertEqual(resp.status_code, 200)

    def test_view_url_uses_correct_template(self):
        resp = self.client.get(reverse(self.url_name))
        self.assertTemplateUsed('blog/index.html')


class SiteUserDetailTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/movie/user/{user_id}'
        cls.url_name = 'user-detail'

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
        self.resp = self.client.get(
                        self.url_path.format(
                            user_id=str(self.site_user.pk)
                        )
                    )

    def test_view_url_exists_at_desired_location(self):
        self.assertEqual(self.resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(
                   reverse(
                       self.url_name,
                       kwargs={
                           'pk': self.site_user.pk,
                       },
                   )
               )
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.assertTemplateUsed(self.resp, 'movie/siteuser_detail.html')


class SiteUserCreateTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/movie/user/create'
        cls.url_name = 'create-user'

    def setUp(self):
        self.resp = self.client.get(self.url_path)

    def test_view_exists_at_desired_location(self):
        resp = self.client.get(self.url_path)
        self.assertEqual(resp.status_code, 200)

    def test_view_exists_at_desired_location(self):
        resp = self.client.get(reverse(self.url_name))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.assertTemplateUsed(self.resp, 'movie/siteuser_form.html')

    def test_create_user_temporarily(self):
        email_address = 'test@example.com'
        password = '12345'
        user_data = {
                        'password': password,
                        'confirm_password': password,
                        'email': email_address,
                        'first_name': 'Super',
                        'last_name': 'John',
                    }
        resp = self.client.post(
                   self.url_path,
                   user_data,
                   follow=True,
               )
        self.assertTrue(User.objects.filter(email=email_address).exists())
        user_status = User.objects.get(email=email_address)
        self.assertFalse(user_status.is_active)

    def test_create_user_temporarily_without_value_in_password(self):
        email_address = 'test@example.com'
        user_data = {
                        'password': '',
                        'confirm_password': '',
                        'email': email_address,
                        'first_name': 'Super',
                        'last_name': 'John',
                    }
        resp = self.client.post(
                   self.url_path,
                   user_data,
                   follow=True,
               )
        self.assertFalse(User.objects.filter(email=email_address).exists())

    def test_redirect_after_create_user_temporarily(self):
        password = '12345'
        user_data = {
                        'password': password,
                        'confirm_password': password,
                        'email': 'test@example.com',
                        'first_name': 'Super',
                        'last_name': 'John',
                    }
        resp = self.client.post(
                   self.url_path,
                   user_data,
               )
        self.assertRedirects(resp, reverse('created-user-temporarily'))

    def test_send_email_to_suggest_to_complete_registration(self):
        email_address = 'test@example.com'
        password = '12345'
        user_data = {
                        'password': password,
                        'confirm_password': password,
                        'email': email_address,
                        'first_name': 'Super',
                        'last_name': 'John',
                    }
        domain = 'www.example.com'
        resp = self.client.post(
                   self.url_path,
                   user_data,
                   SERVER_NAME=domain
               )
        self.assertEqual(len(mail.outbox), 1)

        sended_mail = mail.outbox[0]
        self.assertEqual(sended_mail.to, [user_data['email'], ])
        self.assertEqual(sended_mail.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(sended_mail.subject, 'Registerd temporarily.')

        user = User.objects.get(email=email_address)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        message_body = "Your account has registered temporarily.\n" \
                       "Click below link, then registration complete\n" \
                       "{scheme}://{domain}{path}\n".format(
                            scheme='https',
                            domain=domain,
                            path=reverse(
                                     'created-user-completely',
                                     kwargs={
                                                 'uidb64': uid,
                                                 'token': token,
                                            }
                                 )
                       )
        self.assertEqual(sended_mail.body, message_body)


class SiteUserCreateTemporarilyTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/movie/user/create/temp'
        cls.url_name = 'created-user-temporarily'

    def test_view_exists_at_desired_location(self):
        resp = self.client.get(self.url_path)
        self.assertEqual(resp.status_code, 200)

    def test_view_exists_at_desired_location(self):
        resp = self.client.get(reverse(self.url_name))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(self.url_path)
        self.assertTemplateUsed(resp, 'movie/created_user_temporarily.html')


class SiteUserCreateCompletelyTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/movie/user/create'

    def test_registration_completes_when_confirmation_link_is_clicked(self):
        email_address = 'test@example.com'
        password = '12345'
        user_data = {
                        'password': password,
                        'confirm_password': password,
                        'email': email_address,
                        'first_name': 'Super',
                        'last_name': 'John',
                    }
        domain = 'www.example.com'
        self.client.post(
             self.url_path,
             user_data,
             SERVER_NAME=domain
        )
        user = User.objects.get(email=email_address)
        self.assertFalse(user.is_active)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        path = reverse(
                   'created-user-completely',
                   kwargs={
                               'uidb64': uid,
                               'token': token,
                          }
               )

        resp = self.client.get(path, follow=True)
        user = User.objects.get(email=email_address)
        self.assertTrue(user.is_active)
        self.assertTrue(SiteUser.objects.filter(user=user).exists())
        self.assertRedirects(resp, reverse('login'))


class SiteUserUpdateNameTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.username_url_path = '/movie/user/edit/name'
        cls.username_url_name = 'user-name-edit'

        cls.mail_address1 = 'test1@example.com'
        cls.password1 = '12345'
        cls.first_name1 = 'Super'
        cls.last_name1 = 'John'
        test_user1 = User.objects.create_user(
                         username=cls.mail_address1,
                         password=cls.password1,
                         email=cls.mail_address1,
                         first_name=cls.first_name1,
                         last_name=cls.last_name1,
                     )
        cls.site_user1 = SiteUser.objects.create(
                             user=test_user1,
                             bio='user bio'
                         )

        cls.mail_address2 = 'test2@example.com'
        cls.password2 = '67890'
        cls.first_name2 = 'Super'
        cls.last_name2 = 'Bob'
        test_user2 = User.objects.create_user(
                         username=cls.mail_address2,
                         password=cls.password2,
                         email=cls.mail_address2,
                         first_name=cls.first_name2,
                         last_name=cls.last_name2,
                     )
        cls.site_user2 = SiteUser.objects.create(
                             user=test_user2,
                             bio='user bio'
                         )

    def test_redirec_to_login_page_when_not_logined(self):
        resp = self.client.get(self.username_url_path)
        self.assertRedirects(
            resp,
            '{login_path}?next={next_path}'.format(
                login_path=reverse('login'),
                next_path=self.username_url_path
            )
        )

        self.client.login(username=self.mail_address1, password=self.password1)
        resp = self.client.get(self.username_url_path)
        self.assertEqual(resp.status_code, 200)

    def test_get_edit_page_of_yourself(self):
        self.client.login(username=self.mail_address1, password=self.password1)
        resp = self.client.get(self.username_url_path)
        self.assertEqual(resp.context['object'].username, self.mail_address1)

    def test_view_exists_at_desired_location(self):
        self.client.login(username=self.mail_address1, password=self.password1)
        resp = self.client.get(self.username_url_path)
        self.assertEqual(resp.status_code, 200)

    def test_view_accessible_by_name(self):
        self.client.login(username=self.mail_address1, password=self.password1)
        resp = self.client.get(
                   reverse(
                       self.username_url_name
                   )
               )
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username=self.mail_address1, password=self.password1)
        resp = self.client.get(self.username_url_path)
        self.assertTemplateUsed(resp, 'movie/user_name_form.html')

    def test_input_form_has_current_value_in_default(self):
        self.client.login(username=self.mail_address1, password=self.password1)
        resp = self.client.get(self.username_url_path)
        initials = resp.context['form'].initial
        self.assertEqual(initials['first_name'], self.first_name1)
        self.assertEqual(initials['last_name'], self.last_name1)

    def test_redirect_if_update_comletes(self):
        self.client.login(username=self.mail_address1, password=self.password1)
        resp = self.client.post(
                    self.username_url_path,
                    {
                        'first_name': self.first_name1 + '2',
                        'last_name': self.last_name1 + '2',
                    }
               )
        self.assertRedirects(
            resp,
            reverse(
                'user-detail',
                kwargs={
                            'pk': self.site_user1.pk,
                       }
            )
        )

    def test_update_username(self):
        self.client.login(username=self.mail_address1, password=self.password1)
        resp = self.client.post(
                    self.username_url_path,
                    {
                        'first_name': self.first_name1 + '2',
                        'last_name': self.last_name1 + '2',
                    }
               )
        self.assertRedirects(
            resp,
            reverse(
                'user-detail',
                kwargs={
                            'pk': self.site_user1.pk,
                       }
            )
        )
        updated_siteuser = SiteUser.objects.get(pk=self.site_user1.pk)
        self.assertEqual(updated_siteuser.user.first_name, self.first_name1 + '2')
        self.assertEqual(updated_siteuser.user.last_name, self.last_name1 + '2')


class SiteUserUpdateEmailTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.email_url_path = '/movie/user/edit/email'
        cls.email_url_name = 'user-email-edit'
        cls.change_email_temporarily_url_path = '/movie/user/edit/email/temp'

        cls.mail_address = 'test1@example.com'
        cls.password = '12345'
        cls.first_name = 'Super'
        cls.last_name = 'John'
        test_user = User.objects.create_user(
                        username=cls.mail_address,
                        password=cls.password,
                        email=cls.mail_address,
                        first_name=cls.first_name,
                        last_name=cls.last_name,
                    )
        cls.site_user = SiteUser.objects.create(
                            user=test_user,
                            bio='user bio'
                        )

    def test_redirec_to_login_page_when_not_logined(self):
        resp = self.client.get(self.email_url_path)
        self.assertRedirects(
            resp,
            '{login_path}?next={next_path}'.format(
                login_path=reverse('login'),
                next_path=self.email_url_path
            )
        )

        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.get(self.email_url_path)
        self.assertEqual(resp.status_code, 200)

    def test_get_edit_page_of_yourself(self):
        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.get(self.email_url_path)
        self.assertEqual(resp.context['object'].username, self.mail_address)

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.get(self.email_url_path)
        self.assertEqual(resp.status_code, 200)

    def test_view_accessible_by_name(self):
        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.get(
                    reverse(
                        self.email_url_name
                    )
               )
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.get(self.email_url_path)
        self.assertTemplateUsed(resp, 'movie/user_email_form.html')

    def test_input_form_has_current_value_in_default(self):
        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.get(self.email_url_path)
        initials = resp.context['form'].initial
        self.assertEqual(initials['email'], self.mail_address)

    def test_change_email_address(self):
        self.client.login(username=self.mail_address, password=self.password)
        new_email = 'new@example.com'
        resp = self.client.post(
                    self.email_url_path,
                    {
                         'email': new_email,
                    }
               )
        self.assertRedirects(resp, self.change_email_temporarily_url_path)

    def test_send_email_to_suggest_to_complete_changing_email_address(self):
        self.client.login(username=self.mail_address, password=self.password)
        new_email_address = 'new@example.com'
        domain = 'www.example.com'
        resp = self.client.post(
                    self.email_url_path,
                    {
                         'email': new_email_address,
                    },
                    SERVER_NAME=domain
               )

        self.assertEqual(len(mail.outbox), 1)

        sended_mail = mail.outbox[0]
        self.assertEqual(sended_mail.to, [new_email_address, ])
        self.assertEqual(sended_mail.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(sended_mail.subject, 'Changed Email Address Temporarily.')

        user = User.objects.get(username=self.mail_address)
        token = default_token_generator.make_token(user)
        encoded_new_email_address = urlsafe_base64_encode(force_bytes(new_email_address))
        message_body = "Your email address has changed temporarily.\n" \
                       "Click below link, then change completes\n" \
                       "{scheme}://{domain}{path}\n".format(
                            scheme='https',
                            domain=domain,
                            path=reverse(
                                     'user-email-edit-completely',
                                     kwargs={
                                                 'token': token,
                                                 'new_email': encoded_new_email_address,
                                            }
                                 )
                       )
        """print(sended_mail.body)
        print(message_body)
        """
        self.assertEqual(sended_mail.body, message_body)

    def test_change_email_address_completely_when_click_link(self):
        self.client.login(username=self.mail_address, password=self.password)
        new_email_address = 'new@example.com'
        domain = 'www.example.com'
        resp = self.client.post(
                    self.email_url_path,
                    {
                         'email': new_email_address,
                    },
                    SERVER_NAME=domain
               )
        user = User.objects.get(username=self.mail_address)
        self.assertNotEqual(user.email, new_email_address)

        token = default_token_generator.make_token(user)
        encoded_new_email_address = urlsafe_base64_encode(force_bytes(new_email_address))
        path = reverse(
                    'user-email-edit-completely',
                    kwargs={
                                'token': token,
                                'new_email': encoded_new_email_address,
                           }
               )

        resp = self.client.get(path)
        self.assertTemplateUsed(resp, 'movie/user_email_change_completely.html')

        user = User.objects.get(pk=user.pk)
        self.assertEqual(user.username, new_email_address)
        self.assertEqual(user.email, new_email_address)

    def test_cannot_change_when_another_user_clicks_change_completion_link(self):
        self.client.login(username=self.mail_address, password=self.password)
        new_email_address = 'new@example.com'
        domain = 'www.example.com'
        resp = self.client.post(
                    self.email_url_path,
                    {
                         'email': new_email_address,
                    },
                    SERVER_NAME=domain
               )
        user = User.objects.get(username=self.mail_address)

        token = default_token_generator.make_token(user)
        encoded_new_email_address = urlsafe_base64_encode(force_bytes(new_email_address))
        path = reverse(
                 'user-email-edit-completely',
                 kwargs={
                             'token': token,
                             'new_email': encoded_new_email_address,
                        }
               )

        another_email = 'another@example.com'
        another_password = '12345'
        another_user = User.objects.create_user(
                           username=another_email,
                           password=another_password,
                           first_name='another_first',
                           last_name='another_last'
                       )
        SiteUser.objects.create(user=another_user, bio='another bio')
        another_client = Client()
        another_client.login(username=another_email, password=another_password)
        another_client.get(path)
        user = User.objects.get(username=self.mail_address)
        self.assertNotEqual(user.email, new_email_address)


class SiteUserUpdateBioTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/movie/user/edit/bio'
        cls.url_name = 'user-bio-edit'

        cls.mail_address = 'test1@example.com'
        cls.password = '12345'
        cls.first_name = 'Super'
        cls.last_name = 'John'
        test_user = User.objects.create_user(
                        username=cls.mail_address,
                        password=cls.password,
                        email=cls.mail_address,
                        first_name=cls.first_name,
                        last_name=cls.last_name,
                    )
        cls.site_user = SiteUser.objects.create(
                            user=test_user,
                            bio='user bio'
                        )

    def test_redirect_when_you_dont_login(self):
        resp = self.client.get(self.url_path)
        self.assertRedirects(resp, '/accounts/login/?next=' + self.url_path)

    def test_view_exists_at_desired_location(self):
        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.get(self.url_path)
        self.assertEqual(resp.status_code, 200)

    def test_view_accessible_by_name(self):
        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.get(
                    reverse(
                        self.url_name
                    )
               )
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.get(self.url_path)
        self.assertTemplateUsed(resp, 'movie/siteuser_form.html')


class SiteUserUpdateIndexTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/movie/user/edit'
        cls.url_name = 'user-edit-index'

        cls.mail_address = 'test1@example.com'
        cls.password = '12345'
        cls.first_name = 'Super'
        cls.last_name = 'John'
        test_user = User.objects.create_user(
                        username=cls.mail_address,
                        password=cls.password,
                        email=cls.mail_address,
                        first_name=cls.first_name,
                        last_name=cls.last_name,
                    )
        cls.site_user = SiteUser.objects.create(
                            user=test_user,
                            bio='user bio'
                        )

    def test_redirect_when_you_dont_login(self):
        resp = self.client.get(self.url_path)
        self.assertRedirects(resp, '/accounts/login/?next=' + self.url_path)

    def test_view_exists_at_desired_location(self):
        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.get(self.url_path)
        self.assertEqual(resp.status_code, 200)

    def test_view_accessible_by_name(self):
        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.get(
                    reverse(
                        self.url_name
                    )
               )
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.get(self.url_path)
        self.assertTemplateUsed(resp, 'movie/siteuser_edit_index.html')


class SiteUserDeleteTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/movie/user/delete'
        cls.url_name = 'user-delete'

        cls.mail_address = 'test1@example.com'
        cls.password = '12345'
        cls.first_name = 'Super'
        cls.last_name = 'John'
        test_user = User.objects.create_user(
                        username=cls.mail_address,
                        password=cls.password,
                        email=cls.mail_address,
                        first_name=cls.first_name,
                        last_name=cls.last_name,
                    )
        cls.site_user = SiteUser.objects.create(
                            user=test_user,
                            bio='user bio'
                        )

    def test_redirect_when_you_dont_login(self):
        resp = self.client.get(self.url_path)
        self.assertRedirects(resp, '/accounts/login/?next=' + self.url_path)

    def test_view_exists_at_desired_location(self):
        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.get(self.url_path)
        self.assertEqual(resp.status_code, 200)

    def test_view_accessible_by_name(self):
        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.get(
                    reverse(
                        self.url_name
                    )
               )
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.get(self.url_path)
        self.assertTemplateUsed(resp, 'movie/siteuser_confirm_delete.html')

    def test_delete_user(self):
        self.client.login(username=self.mail_address, password=self.password)
        resp = self.client.post(self.url_path)
        self.assertRedirects(resp, reverse('index'))

        self.assertFalse(SiteUser.objects.filter(user=self.site_user.user).exists())
        self.assertFalse(User.objects.filter(pk=self.site_user.user.pk).exists())


class MovieSearchTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/movie/movies'
        cls.url_name = 'movie-list'

        mail_address = 'test@example.com'
        test_user = User.objects.create_user(
                        username=mail_address,
                        password='12345',
                        email=mail_address,
                        first_name='Super',
                        last_name='John',
                    )
        site_user = SiteUser.objects.create(
                        user=test_user,
                        bio='user bio'
                    )

        upload_file = mock.MagicMock(spec=File, name='FileMock')
        upload_file.name = 'file_name.mp4'
        movie_count = 13
        for num in range(movie_count):
            movie = Movie.objects.create(
                        uploader=site_user,
                        description='movie description',
                        movie_name='movie title ' + str(num),
                        uploaded_file=upload_file,
                    )

    def setUp(self):
        self.resp = self.client.get(self.url_path)

    def test_view_url_exists_at_desired_location(self):
        self.assertEqual(self.resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(
                   reverse(
                       'movie-list'
                   )
               )
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.assertTemplateUsed(self.resp, 'movie/movie_list.html')

    def test_pagenation_is_valid(self):
        self.assertIn('is_paginated', self.resp.context)
        self.assertTrue(self.resp.context['is_paginated'])
        self.assertEqual(len(self.resp.context['movie_list']), 10)

    def test_pagination_is_valid_in_second_page(self):
        resp = self.client.get(self.url_path + '?page=2')
        self.assertEqual(len(resp.context['movie_list']), 3)

    def test_search_movie_name(self):
        resp = self.client.get(self.url_path + '?q=2')
        self.assertEqual(len(resp.context['movie_list']), 2)

    def test_search_movie_name_with_multiple_words(self):
        resp = self.client.get(self.url_path + '?q=2+e')
        self.assertEqual(len(resp.context['movie_list']), 2)


class MovieDetailTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/movie/{movie_id}'
        cls.url_name = 'movie-detail'

        mail_address = 'test@example.com'
        test_user = User.objects.create_user(
                        username=mail_address,
                        password='12345',
                        email=mail_address,
                        first_name='Super',
                        last_name='John',
                    )
        site_user = SiteUser.objects.create(
                        user=test_user,
                        bio='user bio'
                    )

        upload_file = mock.MagicMock(spec=File, name='FileMock')
        upload_file.name = 'file_name.mp4'
        cls.movie = Movie.objects.create(
                         uploader=site_user,
                         description='movie description',
                         movie_name='movie title ',
                         uploaded_file=upload_file,
                     )

    def setUp(self):
        self.resp = self.client.get(
                        self.url_path.format(
                            movie_id=str(self.movie.pk)
                        )
                    )

    def test_view_exists_at_desired_location(self):
        self.assertEqual(self.resp.status_code, 200)

    def test_view_accessible_by_name(self):
        resp = self.client.get(
                   reverse(
                       self.url_name,
                       kwargs={'pk': self.movie.pk, }
                   )
               )
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        self.assertTemplateUsed(self.resp, 'movie/movie_detail.html')


class MovieCreateTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/movie/create'
        cls.url_name = 'upload-movie'
        cls.login_path = '/accounts/login/'
        cls.movie_path = '/movie/{movie_id}'

        cls.mail_address1 = 'test1@example.com'
        cls.password1 = '12345'
        test_user1 = User.objects.create_user(
                         username=cls.mail_address1,
                         password=cls.password1,
                         email=cls.mail_address1,
                         first_name='Super',
                         last_name='John',
                     )
        uploader = SiteUser.objects.create(
                       user=test_user1,
                       bio='user bio'
                   )

    def test_users_redirect_if_not_logged_in(self):
        resp = self.client.get(self.url_path)
        self.assertRedirects(
            resp,
            '{login}?next={source}'.format(
                login=self.login_path,
                source=self.url_path
            )
        )

    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(username=self.mail_address1, password=self.password1)
        resp = self.client.get(self.url_path)
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username=self.mail_address1, password=self.password1)
        resp = self.client.get(reverse(self.url_name))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username=self.mail_address1, password=self.password1)
        resp = self.client.get(reverse(self.url_name))
        self.assertTemplateUsed(resp, 'movie/movie_form.html')

    def test_upload_movie(self):
        login = self.client.login(username=self.mail_address1, password=self.password1)
        upload_file = ContentFile(b'\x00\x00\x00 ftypisom\x00\x00\x02\x00')
        upload_file.name = 'test_movie.mp4'
        resp = self.client.post(
                    self.url_path,
                    {
                        'movie_name': 'Movie Title',
                        'description': 'desc',
                        'uploaded_file': upload_file,
                    },
                    follow=True
               )
        movie_object = Movie.objects.filter().order_by('-post_date')[0]
        self.assertRedirects(
            resp,
            self.movie_path.format(
                movie_id=movie_object.pk
            )
        )

    def test_upload_movie_name_is_random(self):
        login = self.client.login(username=self.mail_address1, password=self.password1)
        upload_file = ContentFile(b'\x00\x00\x00 ftypisom\x00\x00\x02\x00')
        upload_file.name = 'test_movie.mp4'
        resp = self.client.post(
                    self.url_path,
                    {
                        'movie_name': 'Movie Title',
                        'description': 'desc',
                        'uploaded_file': upload_file,
                    },
                    follow=True
               )
        movie_object = Movie.objects.filter().order_by('-post_date')[0]
        uploaded_file_name, uploaded_file_ext = upload_file.name.rsplit('.', 1)
        saved_file_name = os.path.basename(movie_object.uploaded_file.name)
        self.assertNotEqual(saved_file_name.find(uploaded_file_name), 0)


class MovieUpdateTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/movie/{movie_id}/edit'
        cls.url_name = 'movie-edit'

        cls.email_address = 'test@example.com'
        cls.password = 'test@example.com'
        test_user = User.objects.create_user(
                        username=cls.email_address,
                        password=cls.password,
                        email=cls.email_address,
                        first_name='Super',
                        last_name='John',
                    )
        site_user = SiteUser.objects.create(
                        user=test_user,
                        bio='user bio'
                    )

        upload_file = mock.MagicMock(spec=File, name='FileMock')
        upload_file.name = 'file_name.mp4'
        cls.movie = Movie.objects.create(
                        uploader=site_user,
                        description='movie description',
                        movie_name='movie title',
                        uploaded_file=upload_file,
                    )

    def test_redirect_login_page_when_you_has_not_logined(self):
        request_path = self.url_path.format(
                           movie_id=self.movie.pk
                       )
        resp = self.client.get(request_path)
        self.assertRedirects(resp, '/accounts/login/?next=' + request_path)

    def test_view_exists_at_desired_location(self):
        self.client.login(username=self.email_address, password=self.password)
        resp = self.client.get(
                   self.url_path.format(
                       movie_id=self.movie.pk
                   )
               )
        self.assertEqual(resp.status_code, 200)

    def test_view_accessible_by_name(self):
        self.client.login(username=self.email_address, password=self.password)
        resp = self.client.get(
                    reverse(
                        self.url_name,
                        kwargs={
                                    'pk': self.movie.pk,
                               }
                    )
               )
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_desired_template(self):
        self.client.login(username=self.email_address, password=self.password)
        resp = self.client.get(
                   self.url_path.format(
                       movie_id=self.movie.pk
                   )
               )
        self.assertTemplateUsed(resp, 'movie/movie_form.html')

    def test_view_is_not_accessible_by_not_owner(self):
        user2_email_address = 'not-owner@example.com'
        user2_password = '67890'
        user2 = User.objects.create_user(
                    username=user2_email_address,
                    password=user2_password,
                    email=user2_email_address,
                    first_name='first2',
                    last_name='last2'
                )
        siteuser2 = SiteUser.objects.create(user=user2, bio='bio')
        self.client.login(username=user2_email_address, password=user2_password)
        resp = self.client.get(
                   self.url_path.format(
                       movie_id=self.movie.pk
                   )
               )
        self.assertEqual(resp.status_code, 403)

    def test_update_movie_name(self):
        self.client.login(username=self.email_address, password=self.password)
        old_movie_name = self.movie.movie_name
        old_movie_description = self.movie.description
        resp = self.client.post(
                   self.url_path.format(
                       movie_id=self.movie.pk
                   ),
                   {
                        'movie_name': 'new_' + old_movie_name,
                        'description': old_movie_description,
                   }
               )
        new_movie = Movie.objects.get(pk=self.movie.pk)
        self.assertNotEqual(new_movie.movie_name, self.movie.movie_name)
        self.assertEqual(new_movie.description, self.movie.description)

    def test_update_movie_description(self):
        self.client.login(username=self.email_address, password=self.password)
        old_movie_name = self.movie.movie_name
        old_movie_description = self.movie.description
        resp = self.client.post(
                   self.url_path.format(
                       movie_id=self.movie.pk
                   ),
                   {
                        'movie_name': old_movie_name,
                        'description': 'new_' + old_movie_description,
                   }
               )
        new_movie = Movie.objects.get(pk=self.movie.pk)
        self.assertEqual(new_movie.movie_name, self.movie.movie_name)
        self.assertNotEqual(new_movie.description, self.movie.description)

    def test_redirect_to_movie_detail_page_when_update_suceeds(self):
        self.client.login(username=self.email_address, password=self.password)
        old_movie_name = self.movie.movie_name
        old_movie_description = self.movie.description
        resp = self.client.post(
                   self.url_path.format(
                       movie_id=self.movie.pk
                   ),
                   {
                        'movie_name': old_movie_name,
                        'description': 'new_' + old_movie_description,
                   }
               )
        self.assertRedirects(resp, '/movie/' + str(self.movie.pk))


class MovieDeleteTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/movie/{movie_id}/delete'
        cls.url_name = 'movie-delete'

        cls.email_address = 'test@example.com'
        cls.password = 'test@example.com'
        test_user = User.objects.create_user(
                        username=cls.email_address,
                        password=cls.password,
                        email=cls.email_address,
                        first_name='Super',
                        last_name='John',
                    )
        site_user = SiteUser.objects.create(
                        user=test_user,
                        bio='user bio'
                    )

        upload_file = mock.MagicMock(spec=File, name='FileMock')
        upload_file.name = 'file_name.mp4'
        cls.movie = Movie.objects.create(
                        uploader=site_user,
                        description='movie description',
                        movie_name='movie title ',
                        uploaded_file=upload_file,
                    )

    def test_redirect_login_page_when_you_has_not_logined(self):
        request_path = self.url_path.format(
                           movie_id=self.movie.pk
                       )
        resp = self.client.get(request_path)
        self.assertRedirects(resp, '/accounts/login/?next=' + request_path)

    def test_view_exists_at_desired_location(self):
        self.client.login(username=self.email_address, password=self.password)
        resp = self.client.get(
                   self.url_path.format(
                       movie_id=self.movie.pk
                   )
               )
        self.assertEqual(resp.status_code, 200)

    def test_view_accessible_by_name(self):
        self.client.login(username=self.email_address, password=self.password)
        resp = self.client.get(
                    reverse(
                        self.url_name,
                        kwargs={
                                    'pk': self.movie.pk,
                               }
                    )
               )
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_desired_template(self):
        self.client.login(username=self.email_address, password=self.password)
        resp = self.client.get(
                   self.url_path.format(
                       movie_id=self.movie.pk
                   )
               )
        self.assertTemplateUsed(resp, 'movie/movie_confirm_delete.html')

    def test_view_is_not_accessible_by_not_owner(self):
        user2_email_address = 'not-owner@example.com'
        user2_password = '67890'
        user2 = User.objects.create_user(
                    username=user2_email_address,
                    password=user2_password,
                    email=user2_email_address,
                    first_name='first2',
                    last_name='last2'
                )
        siteuser2 = SiteUser.objects.create(user=user2, bio='bio')
        self.client.login(username=user2_email_address, password=user2_password)
        resp = self.client.get(
                   self.url_path.format(
                       movie_id=self.movie.pk
                   )
               )
        self.assertEqual(resp.status_code, 403)

    def test_complete_to_remove_movie(self):
        self.client.login(username=self.email_address, password=self.password)
        resp = self.client.post(
                   self.url_path.format(
                       movie_id=self.movie.pk
                   )
               )
        self.assertRedirects(resp, reverse('user-edit-index'))
        self.assertFalse(Movie.objects.filter(pk=self.movie.pk).exists())


class MovieCommentCreateTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_path = '/movie/{movie_id}/comment'
        cls.url_name = 'create-comment'
        cls.url_redirectd = '/movie/{movie_id}'
        cls.login_path = '/accounts/login/'

        mail_address1 = 'test1@example.com'
        test_user1 = User.objects.create_user(
                         username=mail_address1,
                         password='12345',
                         email=mail_address1,
                         first_name='Super',
                         last_name='John',
                     )
        uploader = SiteUser.objects.create(
                       user=test_user1,
                       bio='user bio'
                   )

        cls.mail_address2 = 'test2@example.com'
        cls.password2 = '12345'
        test_user2 = User.objects.create_user(
                         username=cls.mail_address2,
                         password=cls.password2,
                         email=cls.mail_address2,
                         first_name='Super',
                         last_name='Bob',
                     )
        cls.commenter = SiteUser.objects.create(
                            user=test_user2,
                            bio='user bio'
                        )

        upload_file = mock.MagicMock(spec=File, name='FileMock')
        upload_file.name = 'file_name.mp4'
        cls.movie = Movie.objects.create(
                        uploader=uploader,
                        description='movie description',
                        movie_name='movie title ',
                        uploaded_file=upload_file,
                    )

    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(username=self.mail_address2, password=self.password2)
        resp = self.client.get(
                   self.url_path.format(
                       movie_id=str(self.movie.pk)
                   )
               )
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username=self.mail_address2, password=self.password2)
        resp = self.client.get(
                   reverse(
                       self.url_name,
                       kwargs={'pk': self.movie.pk, }
                   )
               )
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username=self.mail_address2, password=self.password2)
        resp = self.client.get(
                   self.url_path.format(
                       movie_id=str(self.movie.pk)
                   )
               )
        self.assertTemplateUsed(resp, 'movie/comment_form.html')

    def test_view_create_comment(self):
        login = self.client.login(username=self.mail_address2, password=self.password2)
        resp = self.client.post(
                   self.url_path.format(
                       movie_id=str(self.movie.pk)
                   ),
                   {'description': 'comment desc', }
               )
        self.assertRedirects(
            resp,
            self.url_redirectd.format(
                movie_id=str(self.movie.pk)
            )
        )

    def test_redirect_if_not_logined(self):
        resp = self.client.get(self.url_path.format(movie_id=str(self.movie.pk)))
        self.assertRedirects(
            resp,
            '{login}?next={redirect}'.format(
                login=self.login_path,
                redirect=self.url_path.format(
                    movie_id=self.movie.pk
                )
            )
        )


class AcountingTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url_base_path = '/accounts/'
        cls.url_top = '/movie/'

        cls.mail_address1 = 'test1@example.com'
        cls.password1 = '12345'
        test_user1 = User.objects.create_user(
                         username=cls.mail_address1,
                         password=cls.password1,
                         email=cls.mail_address1,
                         first_name='Super',
                         last_name='John',
                     )
        cls.siteuser = SiteUser.objects.create(
                            user=test_user1,
                            bio='user bio'
                       )

    def test_login_view_url_exists_at_desired_location(self):
        resp = self.client.get(self.url_base_path + 'login/')
        self.assertEqual(resp.status_code, 200)

    def test_redirect_after_login_succeeded_top_page(self):
        resp = self.client.post(
                    reverse('login'),
                    {
                        'username': self.mail_address1,
                        'password': self.password1,
                    },
                    follow=True
               )
        self.assertRedirects(resp, self.url_top)

    def test_logout_view_url_exists_at_desired_location(self):
        resp = self.client.get(self.url_base_path + 'logout/')
        self.assertEqual(resp.status_code, 200)
