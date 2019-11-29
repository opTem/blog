from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse
from django.views.generic import FormView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout

from app.models import Publication, Subscription, Rating, Comment
from .forms import CreatePublicationForm, CommentForm


def get_all_new_publications_in_user_subscriptions(user):
    count = 0
    subscriptions = Subscription.objects.filter(subscriber=user)
    for subscription in subscriptions:
        count += subscription.new
    return count


class AuthorizationView(FormView):
    def get(self, request, **kwargs):
        if self.request.user is not None and self.request.user.is_authenticated:
            return redirect('/')
        return render(request, 'app/auth.html', {
            'auth_form': AuthenticationForm(),
            'error': False,
        })

    def post(self, request, **kwargs):
        if self.request.user is not None and self.request.user.is_authenticated:
            return redirect('/')
        authenticated_user = authenticate(
            self.request,
            username=self.request.POST.get('username'),
            password=self.request.POST.get('password')
        )
        login(self.request, authenticated_user)
        if authenticated_user is not None \
                and authenticated_user.is_authenticated:
            return redirect('/')
        return render(self.request, 'app/auth.html', {
            'auth_form': AuthenticationForm(self.request.POST),
            'error': True,
        })


class CreatePublicationView(FormView):
    def get(self, request, **kwargs):
        if self.request.user is None or not self.request.user.is_authenticated:
            return redirect('/auth/')

        new_count = get_all_new_publications_in_user_subscriptions(
            self.request.user)

        return render(self.request, 'app/create_publication.html', {
            'create_publication_form': CreatePublicationForm(),
            'new_count': new_count,
            'view_name': 'create_publication',
        })

    def post(self, request, **kwargs):
        if self.request.user is None or not self.request.user.is_authenticated:
            return redirect('/auth/')
        publication = Publication(blogger=self.request.user,
                                  text=self.request.POST.get('text'),
                                  short_text=self.request.POST.get('short_text'),
                                  name=self.request.POST.get('name'))
        publication.save()

        subscriptions_for_user = Subscription.objects.filter(
            blogger=self.request.user)

        for subscription in subscriptions_for_user:
            subscription.new += 1
            subscription.save()

        return redirect('/')


class GetPublicationsView(FormView):
    def get(self, request, **kwargs):
        if self.request.user is None or not self.request.user.is_authenticated:
            return redirect('/auth/')

        subscriptions = Subscription.objects.filter(subscriber=self.request.user)
        mapped_subscriptions = list(map(
            lambda subscription: subscription.blogger.username,
            subscriptions,
        ))

        only_subscribed = self.request.GET.get('only_subscribed') == 't'

        if only_subscribed:
            publications = Publication.objects.filter(blogger__blogger__in=subscriptions)\
                .order_by('-created')
            for sub in subscriptions:
                sub.new = 0
                sub.save()
        else:
            publications = Publication.objects.all().order_by('-created')

        new_count = get_all_new_publications_in_user_subscriptions(
            self.request.user)

        print(mapped_subscriptions)
        print(len(mapped_subscriptions))

        result_publications = []
        for publ in publications:
            subscribed = False

            for subs in mapped_subscriptions:
                print("Blogger: " + publ.blogger.username)
                print(subs == publ.blogger.username)
                if subs == publ.blogger.username:
                    subscribed = True
                    break

            result_publications.append({
                'id': publ.id,
                'name': publ.name,
                'short_text': publ.short_text,
                'text': publ.text,
                'created': publ.created,
                'blogger': publ.blogger.username,
                'subscribed': subscribed,
                'rating': publ.rating,
                'user_rating': publ.user_rating(self.request.user),
            })
        return render(self.request, 'app/publications.html', {
            'create_publication_form': CreatePublicationForm(),
            'publications': result_publications,
            'subscriptions': mapped_subscriptions,
            'new_count': new_count,
            'view_name': 'sub_pubs' if only_subscribed else 'all_pubs',
        })


class GetPublicationView(FormView):
    def get(self, request, **kwargs):
        if self.request.user is None or not self.request.user.is_authenticated:
            return redirect('/auth/')

        new_count = get_all_new_publications_in_user_subscriptions(
            self.request.user)

        subscriptions = Subscription.objects.filter(subscriber=self.request.user)
        mapped_subscriptions = list(map(
            lambda subscription: subscription.subscriber.username,
            subscriptions,
        ))
        publication = Publication.objects.get(id=self.kwargs.get('publication_id'))

        subscribed = False

        for subs in mapped_subscriptions:
            if subs == publication.blogger.username:
                subscribed = True
                break

        comments = Comment.objects.filter(publication=publication).order_by('-id')

        return render(self.request, 'app/publication.html', {
            'create_publication_form': CreatePublicationForm(),
            'publication': {
                'id': publication.id,
                'name': publication.name,
                'short_text': publication.short_text,
                'text': publication.text,
                'created': publication.created,
                'blogger': publication.blogger.username,
                'subscribed': subscribed,
                'rating': publication.rating,
                'user_rating': publication.user_rating(self.request.user),
            },
            'comment_form': CommentForm(),
            'comments': [
                comment.to_dict() for comment in comments
            ],
            'comments_len': len(comments),
            'subscriptions': mapped_subscriptions,
            'new_count': new_count,
            'view_name': 'publication',
        })


class RatingView(FormView):
    def post(self, request, *args, **kwargs):

        print(self.request.POST.get('publication_id'))
        if self.request.user is None or not self.request.user.is_authenticated:
            return redirect('/auth/')

        publication_id = self.request.POST.get('publication_id')

        publication = Publication.objects.get(id=publication_id)

        if self.request.POST.get('submit') == 'Лайк':
            try:
                rating = Rating.objects.get(publication=publication,
                                            user=self.request.user)
                rating.is_plus = True
                rating.save()
            except Rating.DoesNotExist:
                Rating.objects.create(publication=publication,
                                      user=self.request.user,
                                      is_plus=True)
        elif self.request.POST.get('submit') == 'Дизлайк':
            try:
                rating = Rating.objects.get(publication=publication,
                                            user=self.request.user)
                rating.is_plus = False
                rating.save()
            except Rating.DoesNotExist:
                Rating.objects.create(publication=publication,
                                      user=self.request.user,
                                      is_plus=False)

        return redirect(request.META.get('HTTP_REFERER', '/'))


class SubscribeView(FormView):
    def post(self, request, **kwargs):
        if self.request.user is None or not self.request.user.is_authenticated:
            return redirect('/auth/')

        username = self.request.POST.get('username')

        user = User.objects.get(username=username)

        action = request.POST.get('action')

        print('-------')
        print("Action: " + action)
        print("Subscriber: " + self.request.user.username)
        print("Blogger: " + user.username)
        print('-------')

        if action == 'Подписаться':
            subs = Subscription.objects.filter(subscriber=self.request.user,
                                        blogger=user)
            if len(subs) == 0:
                Subscription.objects.create(subscriber=self.request.user,
                                            blogger=user)
        elif action == 'Отписаться':
            subscriptions = Subscription.objects.filter(subscriber=self.request.user,
                                     blogger=user)
            for sub in subscriptions:
                sub.delete()

        return redirect(request.META.get('HTTP_REFERER', '/'))


class CommentView(FormView):
    def post(self, request, **kwargs):
        if self.request.user is None or not self.request.user.is_authenticated:
            return redirect('/auth/')

        publication_id = self.kwargs.get('publication_id')

        Comment.objects.create(commentator=self.request.user,
                               publication_id=publication_id,
                               text=self.request.POST.get('text'))

        return redirect(request.META.get('HTTP_REFERER', '/'))


class LogoutView(FormView):
    def get(self, request, *args, **kwargs):
        logout(self.request)
        return redirect('/auth/')
