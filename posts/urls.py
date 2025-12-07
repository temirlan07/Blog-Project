from django.urls import path
from . import views
from .feeds import LatestPostsFeed

app_name = 'posts'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post-list'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('search/', views.PostSearchView.as_view(), name='post-search'),
    path('category/<slug:category_slug>/', views.PostListView.as_view(), name='category-posts'),
    path('tag/<slug:tag_slug>/', views.PostListView.as_view(), name='tag-posts'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('rss/', LatestPostsFeed(), name='post-rss'),
]