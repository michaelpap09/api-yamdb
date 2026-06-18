from rest_framework.routers import DefaultRouter
from django.urls import path, include
from django.conf.urls import router

from .views import (
    TitleViewSet,
    CommentViewSet,
    ReviewViewSet,
    CategoryViewSet,
    GenreViewSet
)

router = DefaultRouter()
router.register(r'titles', TitleViewset, basename='titles')


urlpatterns = [
    path('', include(router.urls)),
    path('titles/<int:title_id>/reviews/',
         ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='reviews-list'),
    path('titles/<int:title_id>/reviews/<int:pk>/',
         ReviewViewSet.as_view({'get': 'retrieve',
                                'patch': 'partial_update',
                                'delete': 'destroy'}),
         name='review-detail'),
    path('titles/<int:title_id>/reviews/<int:review_id>/comments/',
         CommentViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='comments-list'),
    path('titles/<int:title_id>/reviews/<int:review_id>/comments/<int:pk>/',
         CommentViewSet.as_view({'get': 'retrieve',
                                 'patch': 'partial_update',
                                 'delete': 'destroy'}),
         name='comment-detail'),
]
