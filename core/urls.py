from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.views import GameViewSet


router = DefaultRouter()
router.register(r"games", GameViewSet, basename="game")

urlpatterns = [
    path("", include(router.urls)),
]
