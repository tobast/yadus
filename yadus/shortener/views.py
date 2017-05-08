from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from .models import ShortUrl


def index(request, created_slug=None, err=None):
    ''' Index page's view '''
    error_texts = {
        'inuse': 'this short text is already used :c',
        'invalid-url': 'please submit a valid URL.',
    }

    if created_slug is not None:
        created_url = request.build_absolute_uri('/' + created_slug)
    else:
        created_url = ''

    context = {
        'created_url': created_url,
        'error_text': error_texts.get(err),
    }

    return render(request, 'shortener/index.html', context)


@csrf_exempt
def submit(request):
    ''' Inserts the request in database '''
    human = request.POST.get('human') is not None

    try:
        url = request.POST['url']
    except KeyError:
        if human:
            return redirect('index')
        return HttpResponseBadRequest('Missing POST field: "url"')

    slug = request.POST.get('slug')

    if slug and ShortUrl.slugExists(slug):
        if human:
            return redirect('index-err', err='inuse')
        return HttpResponseForbidden('Slug already in use')

    try:
        dbEntry = ShortUrl.create(url=url, slug=slug)
    except ValidationError:
        if human:
            return redirect('index-err', err='invalid-url')
        return HttpResponseBadRequest('Invalid url')

    if human:
        return redirect('index-created', created_slug=dbEntry.slug)
    return HttpResponse(request.build_absolute_uri('/' + dbEntry.slug))


def followSlug(request, slug=None):
    ''' Follows the given `slug` '''
    if slug is None:
        return redirect('index')

    url = get_object_or_404(ShortUrl, slug=slug)
    return redirect(url.url)
