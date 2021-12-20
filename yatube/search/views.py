from django.http import JsonResponse
from django.template.loader import render_to_string
from posts.models import Post


def search(request):

    content = {'search_list': ''}
    # This realis AJAX jqury
    # if request.is_ajax() and request.GET['data']:
    #     content = {'search_list': Post.objects.filter(
    #         text__icontains=request.GET['data']),}
    # result = render_to_string('includes/search.html', context=content)

    if request.GET['data']:
        content = {'search_list': Post.objects.filter(
            text__icontains=request.GET['data'])}
    result = render_to_string('includes/search.html', context=content)

    return JsonResponse({'result': result})
