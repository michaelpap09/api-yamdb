from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet, get_token, signup
from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
)

router = DefaultRouter()
router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'genres', GenreViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    path('v1/auth/signup/', signup, name='signup'),
    path('v1/auth/token/', get_token, name='token'),
    path('v1/', include(router.urls)),
    path(
        'v1/titles/<int:title_pk>/reviews/',
        ReviewViewSet.as_view(
            {
                'get': 'list',
                'post': 'create',
            }
        ),
        name='reviews',
    ),
    path(
        'v1/titles/<int:title_pk>/reviews/<int:rev_pk>/',
        ReviewViewSet.as_view(
            {
                'get': 'retrieve',
                'delete': 'destroy',
                'patch': 'partial_update',
            }
        ),
    ),
    path(
        'v1/titles/<int:title_pk>/reviews/<int:rev_pk>/comments/',
        CommentViewSet.as_view(
            {
                'get': 'list',
                'post': 'create',
            }
        ),
    ),
    path(
        'v1/titles/<int:title_pk>/reviews/<int:rev_pk>/comments/<int:com_pk>/',
        CommentViewSet.as_view(
            {
                'get': 'retrieve',
                'delete': 'destroy',
                'patch': 'partial_update',
            }
        ),
    ),
]
