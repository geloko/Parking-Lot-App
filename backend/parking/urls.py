from rest_framework.routers import DefaultRouter
from django.urls import include, path, re_path

from . import views

router = DefaultRouter()

urlpatterns = [
    re_path(r'', include(router.urls)),
    path("", views.index, name="index")
]