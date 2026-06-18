from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
)

router = DefaultRouter()
router.register(r'titles', TitleViewSet)
router.register(r'genre', GenreViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'titles/<int:title_pk>/reviews/',
        ReviewViewSet.as_view(
            {
                'get': 'list',
                'post': 'create',
            }
        ),
        name='reviews'
    ),
    path(
        'titles/<int:title_pk>/reviews/<int:rev_pk>/',
        ReviewViewSet.as_view(
            {
                'get': 'retrieve',
                'delete': 'destroy',
                'patch': 'partial_update',
                'put': 'update',
            }
        ),
    ),
    path(
        'titles/<int:title_pk>/reviews/<int:rev_pk>/comments/',
        CommentViewSet.as_view(
            {
                'get': 'list',
                'post': 'create',
            }
        )
    ),
    path(
        'titles/<int:title_pk>/reviews/<int:rev_pk>/comments/<int:com_pk>/',
        CommentViewSet.as_view(
            {
                'get': 'retrieve',
                'delete': 'destroy',
                'patch': 'partial_update',
                'put': 'update',
            }
        )
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls')),
]
