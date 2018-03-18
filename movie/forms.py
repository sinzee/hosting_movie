import magic
import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from .models import Movie


class MovieUploadForm(ModelForm):

    class Meta:
        model = Movie
        fields = ['movie_name', 'description', 'uploaded_file', ]

    def clean_uploaded_file(self):
        data = self.cleaned_data['uploaded_file']
        data_ext = data.name.rsplit('.')[-1]
        valid_extention = (
                                'mp4',
                          )
        valid_mime = (
                        'video/mp4',
                     )
        if data_ext not in valid_extention:
            raise ValidationError(_('Invalid File Extention - this file is not movie one'))
        mime = magic.from_buffer(data.read(1024), mime=True)

        if mime not in valid_mime:
            raise ValidationError(_('Invalid File Type - this file is not movie one'))

        data.name = str(uuid.uuid4()) + '.' + data_ext
        return data


class SiteUserCreateForm(ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = [
                    'first_name',
                    'last_name',
                    'email',
                    'password',
                 ]

    def __init__(self, *args, **kwargs):
        super(SiteUserCreateForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

        self.fields['password'].required = True
        self.fields['password'].widget = forms.PasswordInput()

    def clean_email(self):
        data = self.cleaned_data['email']

        if User.objects.filter(email=data).exists():
            raise ValidationError(_('Duplicate Email Address - this email address already exists'))
        return data

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('password') == cleaned_data.get('confirm_password'):
            raise ValidationError(_("Password Not Match - password doesn't match"))
        return cleaned_data


class SiteUserUpdateEmailForm(ModelForm):

    class Meta:
        model = User
        fields = [
                    'email',
                 ]

    def clean_email(self):
        data = self.cleaned_data['email']

        if User.objects.filter(email=data).exists():
            raise ValidationError(_('Duplicate Email Address - this email address already exists'))
        return data
