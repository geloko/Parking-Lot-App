from rest_framework.routers import DefaultRouter
from django.urls import include, path, re_path

from . import views

router = DefaultRouter()
router.register(r'mall_parkings', views.MallParkingViewSet)
router.register(r'vehicles', views.VehicleViewSet)
router.register(r'parking_slots', views.ParkingSlotViewSet)
router.register(r'parking_slots_sizes', views.ParkingSlotSizeViewSet)
router.register(r'vehicle_parkings', views.VehicleParkingViewSet)
router.register(r'mall_parkings_slots', views.MallParkingSlotsViewSet)

urlpatterns = [
    re_path(r'', include(router.urls))
]