from drf_yasg.utils import swagger_auto_schema

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from . import models
from . import serializers

class BaseViewSet(viewsets.GenericViewSet, 
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin
):
  # Base view set for table attributes containing the create, read and update actions but not delete.

    def perform_create(self, serializer): 
        """Create a new object"""
        if(serializer.is_valid()):
            content = serializer.save()
            return Response(content, status=status.HTTP_201_CREATED)
        else:
            content = serializer.errors
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    # disable full object updates so that the requests would always pass through the partial update function
    @swagger_auto_schema(auto_schema=None)
    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_403_FORBIDDEN)

class MallParkingViewSet(BaseViewSet):
    queryset = models.MallParking.objects.all()
    serializer_class = serializers.MallParkingSerializer

class VehicleViewSet(BaseViewSet):
    queryset = models.Vehicle.objects.all()
    serializer_class = serializers.VehicleSerializer

class ParkingSlotSizeViewSet(BaseViewSet):
    queryset = models.ParkingSlotSize.objects.all()
    serializer_class = serializers.ParkingSlotSizeSerializer

class ParkingSlotViewSet(BaseViewSet):
    queryset = models.ParkingSlot.objects.all()
    serializer_class = serializers.ParkingSlotSerializer

class VehicleParkingViewSet(BaseViewSet):
    queryset = models.VehicleParking.objects.all()
    serializer_class = serializers.VehicleParkingSerializer


