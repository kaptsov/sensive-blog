from django.contrib import admin
from blog.models import Post, Tag, Comment


@admin.register(Post)
class AdminPost(admin.ModelAdmin):
    raw_id_fields = ['author', 'likes', 'tags']


@admin.register(Comment)
class AdminComment(admin.ModelAdmin):
    raw_id_fields = ['author', 'post']


admin.site.register(Tag)
