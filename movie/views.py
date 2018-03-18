from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.http import (
                            Http404,
                            HttpResponseRedirect,
                        )
from django.template.loader import get_template
from django.shortcuts import (
                                get_object_or_404,
                                render,
                             )
from django.urls import reverse
from django.utils.encoding import (
                                    force_bytes,
                                    force_text,
                                  )
from django.utils.http import (
                                urlsafe_base64_encode,
                                urlsafe_base64_decode,
                              )
from django.views import generic

from .forms import (
                        MovieUploadForm,
                        SiteUserCreateForm,
                        SiteUserUpdateEmailForm,
                   )
from .models import (
                        Comment,
                        Movie,
                        SiteUser,
                    )


def index(request):
    return render(
               request,
               'movie/index.html',
           )


class SiteUserDetailView(generic.DetailView):
    model = SiteUser


class SiteUserCreateView(generic.CreateView):
    model = SiteUser
    form_class = SiteUserCreateForm
    success_url = reverse_lazy('created-user-temporarily')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = user.email
        user.set_password(user.password)
        user.is_active = False
        user.save()

        subject_template = get_template('movie/created_user_temporarily_subject.txt')
        message_body_template = get_template('movie/created_user_temporarily_message_body.txt')
        message_body_context = {
                                    'scheme': 'https',
                                    'domain': get_current_site(self.request).domain,
                                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                    'token': default_token_generator.make_token(user),
                               }
        mail.send_mail(
              subject=subject_template.render(),
              message=message_body_template.render(message_body_context),
              from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list=[user.email, ],
        )

        return super(SiteUserCreateView, self).form_valid(form)


class SiteUserCreateTemporarilyView(generic.TemplateView):
    template_name = 'movie/created_user_temporarily.html'


class SiteUserCreateCompletelyView(generic.TemplateView):
    template_name = 'movie/created_user_completely.html'

    def get(self, request, **kwargs):
        token = kwargs['token']
        uidb64 = kwargs['uidb64']
        uid = force_text(urlsafe_base64_decode(uidb64))

        try:
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user \
           and not user.is_active \
           and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()

            SiteUser.objects.create(user=user)
            return HttpResponseRedirect(reverse('login'))
            # return super(SiteUserCreateCompletelyView, self).get(request, **kwargs)
        else:
            raise Http404


class SiteUserUpdateNameView(LoginRequiredMixin, generic.UpdateView):
    model = User
    fields = [
                'first_name',
                'last_name',
             ]
    template_name = 'movie/user_name_form.html'

    def get_success_url(self):
        siteuser = get_object_or_404(SiteUser, user=self.request.user)
        return reverse('user-detail', kwargs={'pk': siteuser.pk, })

    def get_object(self):
        user = get_object_or_404(User, pk=self.request.user.pk)
        return user


class SiteUserUpdateEmailView(LoginRequiredMixin, generic.UpdateView):
    form_class = SiteUserUpdateEmailForm
    template_name = 'movie/user_email_form.html'

    def get_success_url(self):
        siteuser = get_object_or_404(SiteUser, user=self.request.user)
        return reverse('user-email-edit-temporarily')

    def get_object(self):
        user = get_object_or_404(User, pk=self.request.user.pk)
        return user

    def form_valid(self, form):
        user = self.object
        new_email_address = form.cleaned_data['email']
        subject_template = get_template('movie/change_email_temporarily_subject.txt')
        message_body_template = get_template('movie/change_email_temporarily_message_body.txt')
        message_body_context = {
                                    'scheme': 'https',
                                    'domain': get_current_site(self.request).domain,
                                    'token': default_token_generator.make_token(user),
                                    'new_email': urlsafe_base64_encode(force_bytes(new_email_address)),
                               }
        mail.send_mail(
              subject=subject_template.render(),
              message=message_body_template.render(message_body_context),
              from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list=[new_email_address, ],
        )

        return HttpResponseRedirect(self.get_success_url())
        # return super(SiteUserUpdateEmailView, self).form_valid(form)


class SiteUserUpdateEmailTemporarilyView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'movie/user_email_change_temporarily.html'


class SiteUserUpdateEmailCompletelyView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'movie/user_email_change_completely.html'

    def get(self, request, **kwargs):
        token = kwargs['token']
        new_emailb64 = kwargs['new_email']
        new_email = force_text(urlsafe_base64_decode(new_emailb64))
        user = self.request.user

        if user \
           and default_token_generator.check_token(user, token):
            user.username = new_email
            user.email = new_email
            user.save()
            return super(SiteUserUpdateEmailCompletelyView, self).get(request, **kwargs)
        else:
            raise Http404


class SiteUserUpdateBioView(LoginRequiredMixin, generic.UpdateView):
    model = SiteUser
    fields = [
                'bio',
             ]

    def get_object(self):
        siteuser = get_object_or_404(SiteUser, user=self.request.user)
        return siteuser


class SiteUserUpdateIndexView(LoginRequiredMixin, generic.DetailView):
    model = SiteUser
    template_name = 'movie/siteuser_edit_index.html'

    def get_object(self):
        return get_object_or_404(SiteUser, user=self.request.user)


class SiteUserDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = SiteUser
    success_url = reverse_lazy('index')

    def get_object(self):
        return get_object_or_404(SiteUser, user=self.request.user)

    def post(self, request, *args, **kwargs):
        siteuser = get_object_or_404(SiteUser, user=self.request.user)
        siteuser.delete()
        user = get_object_or_404(User, pk=self.request.user.pk)
        user.delete()
        return HttpResponseRedirect(self.success_url)


class MovieDetailView(generic.DetailView):
    model = Movie


class MovieListView(generic.ListView):
    model = Movie
    paginate_by = 10

    def get_queryset(self):
        queryset = super(MovieListView, self).get_queryset()
        q = self.request.GET.get('q')

        if q:
            for keyward in q.split(' '):
                queryset = queryset.filter(movie_name__icontains=keyward)
            return queryset
        return queryset


class MovieCreateView(LoginRequiredMixin, generic.CreateView):
    model = Movie
    form_class = MovieUploadForm

    def form_valid(self, form):
        form.instance.uploader = get_object_or_404(SiteUser, user_id=self.request.user)
        return super(MovieCreateView, self).form_valid(form)


class MovieUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Movie
    fields = [
                'movie_name',
                'description',
             ]

    def get_object(self):
        movie = super(MovieUpdateView, self).get_object()

        if movie.uploader.user.pk == self.request.user.pk:
            return movie
        else:
            raise PermissionDenied


class MovieDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Movie
    success_url = reverse_lazy('user-edit-index')

    def get_object(self):
        movie = super(MovieDeleteView, self).get_object()

        if movie.uploader.user.pk == self.request.user.pk:
            return movie
        else:
            raise PermissionDenied


class MovieCommentCreateView(LoginRequiredMixin, generic.CreateView):
    model = Comment
    fields = ['description', ]

    def form_valid(self, form):
        form.instance.commenter = get_object_or_404(SiteUser, user_id=self.request.user)
        form.instance.movie = get_object_or_404(Movie, pk=self.kwargs['pk'])
        return super(MovieCommentCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('movie-detail', kwargs={'pk': self.kwargs['pk'], })
