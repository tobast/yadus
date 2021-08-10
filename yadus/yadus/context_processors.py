from django.conf import settings


def app_config(request):
    return {
        "ALLOW_NEW_SHORTENED": settings.ALLOW_NEW_SHORTENED,
    }
