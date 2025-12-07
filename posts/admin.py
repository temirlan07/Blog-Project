from django.contrib import admin
from .models import Post, Category, Tag, Comment, Subscription, Like


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'pub_date']
    list_filter = ['status', 'category', 'is_featured', 'pub_date']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'likes_count', 'reading_time', 'created_at', 'updated_at']
    filter_horizontal = ['tags']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'image', 'image_alt')
        }),
        ('Классификация', {
            'fields': ('category', 'tags', 'author')
        }),
        ('Публикация', {
            'fields': ('status', 'pub_date', 'is_featured', 'allow_comments')
        }),
        ('Статистика', {
            'fields': ('views_count', 'likes_count', 'reading_time'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'post', 'approved', 'is_spam', 'created_at']
    list_filter = ['approved', 'is_spam', 'created_at']
    search_fields = ['author_name', 'content', 'post__title']
    readonly_fields = ['ip_address', 'user_agent', 'created_at']
    actions = ['approve_comments', 'reject_comments']

    def approve_comments(self, request, queryset):
        queryset.update(approved=True, is_spam=False)

    approve_comments.short_description = 'Одобрить выбранные комментарии'

    def reject_comments(self, request, queryset):
        queryset.update(approved=False)

    reject_comments.short_description = 'Отклонить выбранные комментарии'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'confirmed_at', 'created_at']
    list_filter = ['is_active', 'confirmed_at']
    search_fields = ['email']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__title']