from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import os


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-адрес")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='children', verbose_name="Родительская категория")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category-posts', kwargs={'category_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название тега")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="URL-адрес")
    description = models.TextField(blank=True, verbose_name="Описание тега")
    color = models.CharField(max_length=7, default='#6c757d', verbose_name="Цвет тега")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag-posts', kwargs={'tag_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


def post_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{slugify(instance.title)}_{instance.pk}.{ext}"
    return os.path.join('posts/images', filename)


class Post(TimeStampedModel):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Черновик'),
        (STATUS_PUBLISHED, 'Опубликован'),
        (STATUS_ARCHIVED, 'В архиве'),
    ]

    title = models.CharField(max_length=200, verbose_name="Заголовок поста")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL-адрес")
    content = models.TextField(verbose_name="Содержание поста")
    excerpt = models.TextField(max_length=500, blank=True, verbose_name="Краткое описание")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    image = models.ImageField(upload_to=post_image_path, blank=True, null=True, verbose_name="Главное изображение")
    image_alt = models.CharField(max_length=200, blank=True, verbose_name="Alt текст изображения")

    pub_date = models.DateTimeField(default=timezone.now, verbose_name="Дата публикации")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуемый пост")
    allow_comments = models.BooleanField(default=True, verbose_name="Разрешить комментарии")

    views_count = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")
    likes_count = models.PositiveIntegerField(default=0, verbose_name="Количество лайков")
    reading_time = models.PositiveIntegerField(default=0, verbose_name="Время чтения (минуты)")

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ['-pub_date', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        word_count = len(self.content.split())
        self.reading_time = max(1, word_count // 200)

        if not self.excerpt and self.content:
            self.excerpt = self.content[:497] + '...' if len(self.content) > 500 else self.content

        super().save(*args, **kwargs)

    @property
    def is_published(self):
        return (self.status == self.STATUS_PUBLISHED and
                self.pub_date <= timezone.now())

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])


class Comment(TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100, verbose_name="Имя автора")
    author_email = models.EmailField(verbose_name="Email автора")
    author_website = models.URLField(blank=True, verbose_name="Веб-сайт автора")
    content = models.TextField(verbose_name="Текст комментария")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP-адрес")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")

    approved = models.BooleanField(default=False, verbose_name="Одобрен")
    is_spam = models.BooleanField(default=False, verbose_name="Спам")

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='replies', verbose_name="Родительский комментарий")
    depth = models.PositiveIntegerField(default=0, verbose_name="Уровень вложенности")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-created_at']

    def __str__(self):
        return f"Комментарий от {self.author_name} к посту '{self.post.title}'"

    def save(self, *args, **kwargs):
        if self.parent:
            self.depth = self.parent.depth + 1
        super().save(*args, **kwargs)


class Subscription(TimeStampedModel):
    email = models.EmailField(unique=True, verbose_name="Email адрес")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    confirmation_token = models.CharField(max_length=64, blank=True, verbose_name="Токен подтверждения")
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата подтверждения")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP-адрес подписки")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return self.email


class Like(TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes')
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        unique_together = ['post', 'user']

    def __str__(self):
        return f"Лайк от {self.user.username} к посту '{self.post.title}'"