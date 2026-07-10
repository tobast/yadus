"""yadus URL Configuration"""

from django.urls import re_path, path
from django.contrib import admin
import shortener.views

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r"^$", shortener.views.index, name="index"),
    re_path(r"^\+error/(?P<err>[\w-]+)$", shortener.views.index, name="index-err"),
    re_path(
        r"^\+created/(?P<created_slug>[\w-]+)$",
        shortener.views.index,
        name="index-created",
    ),
    re_path(r"^\+submit$", shortener.views.submit, name="submit"),
    re_path(r"^(?P<slug>[\w-]+)$", shortener.views.followSlug, name="follow"),
]

handler404 = shortener.views.err404
