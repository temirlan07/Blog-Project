from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import PostViewSet, CategoryViewSet, TagViewSet, CommentViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'subscriptions', SubscriptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]