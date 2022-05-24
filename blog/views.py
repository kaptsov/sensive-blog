from django.db.models import Count, Prefetch
from django.shortcuts import render

from blog.models import Comment, Post, Tag


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.num_posts,
    }


def get_tag_prefetch():
    return Prefetch('tags', Tag.objects.annotate(num_posts=Count('posts')))


def index(request):

    most_popular_posts = Post.objects\
        .popular()\
        .prefetch_related('author')\
        .prefetch_related(get_tag_prefetch())[:5]\
        .fetch_with_comments_count()

    most_fresh_posts = Post.objects\
        .fresh()\
        .prefetch_related('author') \
        .prefetch_related(get_tag_prefetch())[:5] \
        .fetch_with_comments_count()

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):

    post = Post.objects\
        .select_related('author')\
        .annotate(num_likes=Count('likes'))\
        .get(slug=slug)

    most_popular_posts = Post.objects\
        .popular()\
        .prefetch_related('author')\
        .prefetch_related(get_tag_prefetch())[:5]\
        .fetch_with_comments_count()

    tags = Tag.objects.popular()
    most_popular_tags = Tag.objects.popular()[:5]
    related_tags = tags.filter(posts__in=[post])

    comments = Comment.objects.select_related('author').all()
    post_comments = comments.filter(post=post)

    likes_amount = post.num_likes

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": post_comments,
        "likes_amount": likes_amount,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": related_tags,
    }

    context = {
        "post": serialized_post,
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, "post-details.html", context)


def tag_filter(request, tag_title):

    tag = Tag.objects.get(title=tag_title)
    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = Post.objects\
        .popular()\
        .prefetch_related('author')\
        .prefetch_related(get_tag_prefetch())[:5]\
        .fetch_with_comments_count()

    related_posts = tag.posts\
        .prefetch_related('author')\
        .prefetch_related(get_tag_prefetch())[:20]\
        .fetch_with_comments_count()

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
