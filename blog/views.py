from django.shortcuts import render, redirect, get_list_or_404
from .models import Category, Tag, Post, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import PostForm, CommentForm
# Create your views here.

def post_list(request):
    categoryQ = request.GET.get('category')
    tagQ = request.GET.get('tag')
    searchQ = request.GET.get('q')

    posts = Post.objects.all()

    if categoryQ:
        posts = posts.filter(category__name = categoryQ)
    if tagQ:
        posts = posts.filter(tag__name = tagQ)
    if searchQ:
        posts = posts.filter(
            Q(title__icontains = searchQ)
            |Q(content__icontains = searchQ)
            |Q(tag__name__icontains = searchQ)
            |Q(category__name__icontains = searchQ)
        ).distinct()

    paginator = Paginator(posts, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'tag': Tag.objects.all(),
        'search_query': searchQ,
        'category_query': categoryQ,
        'tag_query': tagQ,
    }
    return render(request, '', context)

def post_detail(request, id):
    post = get_list_or_404(Post, id=id)
    if request.method == 'POST':
        comment_form = CommentForm(request.Post)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = comment.user
            comment.save()
            return redirect('', id=post.id)
    else:
        comment_form = CommentForm()
    comments = post.comment_set.all()
    is_liked = post.liked_users.filter(id=request.user.id).exists()
    like_count = post.liked_users.count()

    context = {
        'post': post,
        'categories': Category.objects.all(),
        'tag': Tag.objects.all(),
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
        'like_count': like_count
    }
    post.view_count += 1
    post.save()

    return render(request, '', context)


def like_post(request, id):
    post = get_list_or_404(Post, id=id)
    if post.liked_users.filter(id=request.user.id):
        post.liked_users.remove(request.user)
    else:
        post.liked_users.add(request.user)
    return redirect('', post.id)

def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('')
    else:
        form = PostForm()
    return render(request, '', {'form': form})

def post_update(request, id):
    post = get_list_or_404(Post, id=id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('', id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, '', {'form': form})

def post_delete(request, id):
    post = get_list_or_404(Post, id=id)
    post.delete()
    return redirect('')