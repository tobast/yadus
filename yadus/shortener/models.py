"""
Django DB models for Yadus
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import string
import random
import urllib
import re


class BlacklistedDomain(models.Model):
    """ List of blacklisted models """

    domain = models.CharField(max_length=512)
    is_spam = models.BooleanField(default=True)

    def __str__(self):
        return "{}{}".format(self.domain, " (SPAM)" if self.is_spam else "")


class UserAgent(models.Model):
    """ User agents encountered in the wild """

    user_agent = models.TextField(unique=True)

    @staticmethod
    def normalize(user_agent):
        return user_agent.strip().lower()

    def save(self, *args, **kwargs):
        self.user_agent = self.normalize(self.user_agent)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user_agent


class ShortUrlMetadata(models.Model):
    """ Metadata around a shortened URL that may be collected """

    short_url = models.OneToOneField(
        "ShortUrl", on_delete=models.CASCADE, related_name="metadata"
    )

    user_agent = models.ForeignKey(UserAgent, on_delete=models.CASCADE)

    @classmethod
    def create(cls, for_url, request):
        user_agent, _ = UserAgent.objects.get_or_create(
            user_agent=UserAgent.normalize(request.META["HTTP_USER_AGENT"])
        )
        meta = cls(short_url=for_url, user_agent=user_agent)
        meta.save()

    def __str__(self):
        return "Metadata for {}".format(self.short_url.slug)


class ShortUrl(models.Model):
    """ Shortened URL model """

    slug = models.SlugField(allow_unicode=False)
    url = models.URLField(max_length=settings.MAX_URL_LENGTH)

    date = models.DateTimeField()

    is_spam = models.BooleanField(
        default=False, help_text="Is this link considered spam and disabled?"
    )
    enabled = models.BooleanField(
        default=True, help_text="Is this shortened link disabled?"
    )

    # An entry is considered spam if at least one of the following group of REs
    # matches for all its REs (ie. OR(AND(re.fullmatch)))
    spam_slug_re = [
        [re.compile(r"[a-zA-Z0-9_-]+[0-9]{3,7}"), re.compile(r".*[a-zA-Z].*")],
    ]

    def __str__(self):
        return "{} → {}".format(self.slug, self.url)

    def clean(self):
        """ Validation """
        super().clean()
        self.spam_check()

    def spam_check(self):
        """ Checks the ShortUrl for spam and update flags """
        is_blocked = not self.enabled
        is_spam = self.is_spam

        # Blacklisted domains check
        parsed_url = urllib.parse.urlparse(self.url)
        cur_domain = parsed_url.netloc.lower()
        for blacklisted in BlacklistedDomain.objects.all():
            if blacklisted.domain in cur_domain:
                is_blocked = True
                is_spam = is_spam or blacklisted.is_spam

                if is_spam:
                    break

        # Slug pattern check
        if len(self.slug) != settings.SLUG_LENGTH:
            for re_group in self.spam_slug_re:
                matching = True
                for cur_re in re_group:
                    if not cur_re.fullmatch(self.slug):
                        matching = False
                        break
                if matching:
                    is_blocked = True
                    is_spam = True
                    break

        changed = (self.enabled == is_blocked) or (self.is_spam != is_spam)
        self.enabled = not is_blocked
        self.is_spam = is_spam

        return changed

    @staticmethod
    def slugExists(slug):
        return ShortUrl.objects.filter(slug=slug).exists()

    @staticmethod
    def create(url, slug=None, request=None):
        """ Adds a ShortUrl entry in the database and returns it. If `slug` is
        `None` (default), picks a random slug.
        If the request is passed and the object is identified as spam, some metadata
        will be saved. """

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
        entry = ShortUrl(url=url, slug=slug, date=timezone.now())
        entry.full_clean()
        entry.save()

        if entry.is_spam and request:
            ShortUrlMetadata.create(entry, request)

        return entry
