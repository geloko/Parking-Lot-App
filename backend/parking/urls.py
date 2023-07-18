from rest_framework.routers import DefaultRouter
from django.urls import include, path, re_path

from . import views

router = DefaultRouter()
router.register(r'mall_parkings', views.MallParkingViewSet)
router.register(r'vehicles', views.VehicleViewSet)
router.register(r'parking_slots', views.ParkingSlotViewSet)
router.register(r'parking_slots_sizes', views.ParkingSlotSizeViewSet)
router.register(r'vehicle_parkings', views.VehicleParkingViewSet)
router.register(r'mall_parking_slots', views.MallParkingSlotsViewSet)
# router.register(r'mall_parking_slots/view', views.VehicleParkingViewSet)
# router.register(r'mall_parking_slots/entry', views.VehicleParkingEntryViewSet)
# router.register(r'mall_parking_slots/exit', views.VehicleParkingExitViewSet)

urlpatterns = [
    path('mall_parking_slots/view', views.VehicleParkingViewSet.as_view({'get': 'list'})),
    path('mall_parking_slots/view/<int:pk>', views.VehicleParkingViewSet.as_view({'get': 'retrieve'})),
    path('mall_parking_slots/entry', views.VehicleParkingEntryViewSet.as_view({'post': 'create'})),
    path('mall_parking_slots/exit', views.VehicleParkingExitViewSet.as_view({'patch': 'partial_update'})),
    re_path(r'', include(router.urls))
]