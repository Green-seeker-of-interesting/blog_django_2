from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.views.generic import ListView
from django.core.mail import send_mail
from django.db.models import Count

from taggit.models import Tag

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 4
    template_name = 'blog/post/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['number_post'] = [
            x + 1 for x in range(context['paginator'].num_pages)]
        context['number_ral'] = context['page_obj'].number
        context['my_tags'] = get_list_or_404(Tag)
        return context


def post_list_with_tag(request: HttpRequest, tag_slug=None) -> HttpResponse:
    object_list = Post.published.all()
    tags = get_object_or_404(Tag, slug=tag_slug)
    object_list = object_list.filter(tags__in=[tags])
    return render(request, 'blog/post/list.html',
                  {'posts': object_list,
                   'tag': tags})


def post_detail(request: HttpRequest, year: int, month: int, day: int, post: str) -> HttpResponse:
    # исходные данные
    post: Post = get_object_or_404(Post, slug=post, status='published',
                                   publish__year=year, publish__month=month, publish__day=day)
    comments = post.comments.filter(active=True)
    
    # форма коментариев
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    # Рекомендации
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
        .order_by('-same_tags', '-publish')[:4]


    return render(request, 'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form,
                   'similar_posts': similar_posts,})


def post_share(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id, status='published')
    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            print(cd)
            subject = '{} ({}) recommends you reading "{}"'.format(
                cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s coments:{}'.format(
                post.title, post_url, cd['name'], cd['coments'])

            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True

    form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
