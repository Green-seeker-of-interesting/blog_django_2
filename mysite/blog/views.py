from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_list_or_404
from django.views.generic import ListView
from django.core.mail import send_mail

from .models import Post
from .forms import EmailPostForm


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

        return context


def post_detail(request: HttpRequest, year: int, month: int, day: int, post: str) -> HttpResponse:
    post = get_list_or_404(Post, slug=post, status='published',
                           publish__year=year, publish__month=month, publish__day=day)
    return render(request, 'blog/post/detail.html', {'post': post[0]})


def post_share(request: HttpRequest, post_id: int):
    post = get_list_or_404(Post, pk=post_id, status='published')[0]
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
