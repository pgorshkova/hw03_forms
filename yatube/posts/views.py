from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from .models import Group, Post, User
from .forms import PostForm
from django.shortcuts import redirect


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10) 

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context) 


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': post_list,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)

def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.select_related('author')
    post_count = author_posts.count()
    paginator = Paginator(author_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author' : author,
        'post_count' : post_count,
        'page_obj' : page_obj
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    pub_date = post.pub_date
    post_title = post.text[:30]
    author = post.author
    author_post = author.posts.all().count()
    context = {
        "post": post,
        "post_title": post_title,
        "pub_date": pub_date,
        "author": author,
        "author_post": author_post,
    }
    return render(request, 'posts/post_detail.html', context)

def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author.username)
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form':form})

def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    author = post.author
    if request.user == author:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post.save()
                return redirect('posts:post_detail', post_id)
            context = {
                'form':form,
                'post':post
            }
            return render(request, 'posts/create_post.html', context)
        else:
            form = PostForm(instance=post)
            context = {
                'form':form,
                'post':post,
                'is_edit':is_edit
            }
            return render(request, 'posts/create_post.html', context)
    return redirect('posts:post_detail', post_id)
