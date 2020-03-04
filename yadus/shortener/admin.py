from django.contrib import admin
from .models import ShortUrl, BlacklistedDomain, UserAgent, ShortUrlMetadata

admin.site.register(ShortUrl)
admin.site.register(BlacklistedDomain)
admin.site.register(UserAgent)
admin.site.register(ShortUrlMetadata)
