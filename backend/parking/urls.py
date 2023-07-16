from rest_framework.routers import DefaultRouter
from django.conf.urls import url
from django.urls import include

import views

router = DefaultRouter()

urlpatterns = [
    url(r'', include(router.urls))
]