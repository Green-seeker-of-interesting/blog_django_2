from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_list_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Post


def post_list(request: HttpRequest) -> HttpResponse:
    posts = Post.published.all()
    paginator = Paginator(posts, 3)
    page: str = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', 
    {
        'page': page, 
        'posts': posts,
        'number_post' : [x + 1 for x in range(paginator.num_pages)],
        'number_ral' : int(page)
    })


def post_detail(request: HttpRequest, year: int, month: int, day: int, post: str) -> HttpResponse:
    post = get_list_or_404(Post, slug=post, status='published',
                           publish__year=year, publish__month=month, publish__day=day)
    return render(request, 'blog/post/detail.html', {'post': post[0]})
