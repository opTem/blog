from django.db import models
from django.contrib.auth.models import User


class Subscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriber')
    blogger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogger')
    new = models.IntegerField(default=0)


class Publication(models.Model):
    created = models.DateTimeField(verbose_name="Дата создания",
                                   auto_now_add=True)
    modified = models.DateTimeField(verbose_name="Дата модификации",
                                    auto_now=True)
    blogger = models.ForeignKey(User, verbose_name="Блоггер",
                                on_delete=models.CASCADE)
    name = models.CharField(max_length=64, blank=True)
    text = models.TextField(verbose_name="Текст публикации")
    short_text = models.TextField(verbose_name="Текст публикации", blank=True)

    @property
    def rating(self):
        ratings = Rating.objects.filter(publication=self)
        result = 0

        for rating in ratings:
            result += rating.value

        return result

    def user_rating(self, user):
        rating = None
        try:
            rating = Rating.objects.get(publication=self, user=user)
            rating = {
                'is_plus': rating.is_plus,
            }
        except Rating.DoesNotExist:
            pass
        return rating


class Comment(models.Model):
    created = models.DateTimeField(verbose_name="Дата создания",
                                   auto_now_add=True)
    commentator = models.ForeignKey(User, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, blank=True, null=True)
    text = models.TextField()

    def to_dict(self):
        return {
            'created': self.created,
            'commentator': self.commentator.username,
            'text': self.text,
        }


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    is_plus = models.BooleanField()

    @property
    def value(self):
        return 1 if self.is_plus else -1
