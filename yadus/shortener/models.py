"""
Django DB models for Yadus
"""

from django.db import models
from django.conf import settings


class ShortUrl(models.Model):
    """ Shortened URL model """
    slug = models.SlugField(allow_unicode=True)
    url = models.URLField(max_length=settings.MAX_URL_LENGTH)

    def __str__(self):
        return self.slug
