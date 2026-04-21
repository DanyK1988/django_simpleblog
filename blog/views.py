from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import Post
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
import ssl
import certifi
from taggit.models import Tag

ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

def post_share(request, post_id):
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED,)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s ({cd['email']}) comments: {cd['comments']}"
            send_mail(subject, message, settings.EMAIL_HOST_USER,
                      [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, "sent": sent})


def post_list(request, tag_slug=None):
    all_posts = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        all_posts = all_posts.filter(tags=tag)
    paginator = Paginator(all_posts, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts,
                            'tag': tag})


def post_detail(request, year, month, day, slug):
    post = get_object_or_404(Post,
                              status=Post.Status.PUBLISHED,
                             slug=slug,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)
    form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids) \
        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                            'comments': comments,
                            'form': form,
                            'similar_posts': similar_posts})

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    comment = None

    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(request, 'blog/post/comment.html', {'post': post,
                                                      'form': form,
                                                      'comment': comment})
