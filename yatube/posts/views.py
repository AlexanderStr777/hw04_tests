# posts/views.py
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render, reverse

from .forms import PostForm
from .models import Group, Post

User = get_user_model()


# Главная страница
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGINATOR_VALUE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    title = 'Последние обновления на сайте'
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/index.html', context)


# Cтраницы, на которых будут посты, отфильтрованные по группам
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    post_list = group.group.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


# Страницы пользователя
def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, settings.PAGINATOR_VALUE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


# Страница записи
def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    author = post.author
    title = post.text[:31]
    context = {
        'post': post,
        'author': author,
        'title': title,
    }
    return render(request, 'posts/post_detail.html', context)


# Страницы создания поста
@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        listing = form.save(commit=False)
        listing.author = request.user
        listing.save()

        return redirect(
            reverse('posts:profile', args=[request.user.username]),
        )

    return render(request, 'posts/create_post.html', {'form': form})


# Страница редактирования поста
@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    is_edit = True
    form = PostForm(request.POST or None, instance=post)
    if author == request.user:
        if request.method == 'POST':
            if form.is_valid():
                form.save()

                return redirect(
                    reverse('posts:post_detail', args=[post_id])
                )
            context = {
                'form': form,
                'is_edit': is_edit,
            }

            return render(request, 'posts/create_post.html', context)

        context = {
            'form': form,
            'is_edit': is_edit,
        }
        return render(request, 'posts/create_post.html', context)

    return redirect(reverse('posts:post_detail', args=[post_id]))
