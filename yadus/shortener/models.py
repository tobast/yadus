"""
Django DB models for Yadus
"""

from django.db import models
from django.conf import settings
import string
import random


class ShortUrl(models.Model):
    """ Shortened URL model """
    slug = models.SlugField(allow_unicode=True)
    url = models.URLField(max_length=settings.MAX_URL_LENGTH)

    def __str__(self):
        return self.slug

    @staticmethod
    def slugExists(slug):
        return ShortUrl.objects.filter(slug=slug).exists()

    @staticmethod
    def create(url, slug=None):
        ''' Adds a ShortUrl entry in the database and returns it. If `slug` is
        `None` (default), picks a random slug. '''

        def randomSlug():
            ''' Generates a random unused slug '''
            def nextRandom():
                return ''.join(random.choices(charset, k=settings.SLUG_LENGTH))
            charset = string.ascii_letters + string.digits + '-_'
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
