from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import TitleViewset

router = DefaultRouter()
router.register(r'titles', TitleViewset, basename='titles')

urlpatterns = [
    path('', include(router.urls)),
]