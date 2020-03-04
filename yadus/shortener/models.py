"""
Django DB models for Yadus
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import string
import random


class ShortUrl(models.Model):
    """ Shortened URL model """

    slug = models.SlugField(allow_unicode=False)
    url = models.URLField(max_length=settings.MAX_URL_LENGTH)

    is_spam = models.BooleanField(
        default=False, help_text="Is this link considered spam and disabled?"
    )
    enabled = models.BooleanField(
        default=True, help_text="Is this shortened link disabled?"
    )

    def __str__(self):
        return "{} → {}".format(self.slug, self.url)

    @staticmethod
    def slugExists(slug):
        return ShortUrl.objects.filter(slug=slug).exists()

    @staticmethod
    def create(url, slug=None):
        """ Adds a ShortUrl entry in the database and returns it. If `slug` is
        `None` (default), picks a random slug. """

        def randomSlug():
            """ Generates a random unused slug """

            def nextRandom():
                return "".join(
                    [random.choice(charset) for _ in range(settings.SLUG_LENGTH)]
                )

            charset = string.ascii_letters + string.digits + "-_"
            out = nextRandom()
            while ShortUrl.slugExists(out):
                out = nextRandom()
            return out

        if not slug:
            slug = randomSlug()
        entry = ShortUrl(url=url, slug=slug)
        entry.full_clean()
        entry.save()
        return entry


class UserAgent(models.Model):
    """ User agents encountered in the wild """

    user_agent = models.TextField()

    @staticmethod
    def normalize(user_agent):
        return user_agent.strip().lower()

    def save(self, *args, **kwargs):
        self.user_agent = self.normalize(self.user_agent)
        super().save(*args, **kwargs)


class ShortUrlMetadata(models.Model):
    """ Metadata around a shortened URL that may be collected """

    short_url = models.OneToOneField(
        ShortUrl, on_delete=models.CASCADE, related_name="metadata"
    )

    date = models.DateTimeField()
    user_agent = models.ForeignKey(UserAgent, on_delete=models.CASCADE)

    @classmethod
    def create(cls, for_url, request, date=None):
        if date is None:
            date = timezone.now()
        user_agent = UserAgent.objects.get_or_create(
            user_agent=request.META["HTTP_USER_AGENT"]
        )
        meta = cls(short_url=for_url, date=date, user_agent=user_agent)
        meta.save()
