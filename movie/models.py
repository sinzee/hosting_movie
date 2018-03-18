from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone


class SiteUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    bio = models.TextField(max_length=1000, help_text="Enter your bio details here.")

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'pk': str(self.id), })

    def __str__(self):
        return '{first_name} {last_name}'.format(
                   first_name=self.user.first_name,
                   last_name=self.user.last_name
               )


class Movie(models.Model):
    uploader = models.ForeignKey(
                 SiteUser,
                 on_delete=models.CASCADE,
                 null=True
               )
    movie_name = models.CharField(max_length=100, help_text="Enter your movie name.")
    description = models.TextField(max_length=1000, help_text="Enter your movie description.")
    uploaded_file = models.FileField(upload_to='files/%Y/%m/%d')
    post_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['post_date', 'movie_name', ]

    def get_absolute_url(self):
        return reverse('movie-detail', kwargs={'pk': str(self.id), })

    def __str__(self):
        return self.movie_name


@receiver(post_delete, sender=Movie)
def remove_file(sender, instance, **kwargs):
    instance.uploaded_file.storage.delete(instance.uploaded_file.path)


class Comment(models.Model):
    movie = models.ForeignKey(
                Movie,
                on_delete=models.CASCADE,
            )
    commenter = models.ForeignKey(
                    SiteUser,
                    on_delete=models.SET_NULL,
                    null=True
                )
    description = models.TextField(max_length=250, help_text="Enter your comment to movie.")
    post_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        limit_size = 75
        if len(self.description) > limit_size:
            return self.description[:limit_size]
        else:
            return self.description
