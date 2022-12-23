from django.contrib import admin

from .models import Comment, Post


@admin.register(Post)
class AdminPost(admin.ModelAdmin):
    list_display = (
        'author',
        'title',
        'text',
        'created',
        'updated',
        'status',
        'tag_list',
    )
    list_filter = ('author', 'status')
    search_fields = ('author', 'title', 'text')

    def tag_list(self, obj):
        return u', '.join(o.name for o in obj.tags.all())


@admin.register(Comment)
class AdminComment(admin.ModelAdmin):
    list_display = ('author', 'post', 'text', 'created', 'updated', 'status')
    list_filter = ('status', 'created')
    search_fields = ('author', 'post', 'text')
