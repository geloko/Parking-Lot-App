from drf_yasg.utils import swagger_auto_schema

from rest_framework import viewsets, mixins, status, generics
from rest_framework.response import Response

from . import models
from . import serializers

# Base view set for table attributes containing the create, read and update actions but not delete.
class BaseViewSet(viewsets.GenericViewSet, 
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin
):
    def perform_create(self, serializer): 
        if(serializer.is_valid()):
            content = serializer.save()
            return Response(content, status=status.HTTP_201_CREATED)
        else:
            content = serializer.errors
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
            
    # disable full object updates so that the requests would always pass through the partial update function
    @swagger_auto_schema(auto_schema=None)
    def update(self):
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

class VehicleParkingViewSet(viewsets.GenericViewSet, 
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    queryset = models.VehicleParking.objects.all()
    serializer_class = serializers.VehicleParkingSerializer

class VehicleParkingExitViewSet(viewsets.GenericViewSet,
    mixins.UpdateModelMixin
):
    queryset = models.VehicleParking.objects.all()
    serializer_class = serializers.VehicleParkingSerializer

    # disable full object updates so that the requests would always pass through the partial update function
    @swagger_auto_schema(auto_schema=None)
    def update(self):
        return Response(status=status.HTTP_403_FORBIDDEN)

class VehicleParkingEntryViewSet(viewsets.GenericViewSet, 
    mixins.CreateModelMixin,
):
    queryset = models.VehicleParking.objects.all()
    serializer_class = serializers.VehicleParkingEntrySerializer

class MallParkingSlotsViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin
):
    queryset = models.MallParking.objects.all()
    serializer_class = serializers.MallParkingSlotsSerializer

    def perform_create(self, serializer): 
        if(serializer.is_valid()):
            content = serializer.save()
            return Response(content, status=status.HTTP_201_CREATED)
        else:
            content = serializer.errors
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        mall_parking = models.MallParking.objects.get(pk=pk)
        mall_parking_serializer = serializers.MallParkingSerializer(mall_parking)
        parking_slots = models.ParkingSlot.objects.all()
        parking_slots_serializer = serializers.ParkingSlotSerializer(parking_slots, many=True)

        # TODO: Fix bug in passing data for retrieve

        return Response(
            {
                mall_parking: mall_parking_serializer.data,
                parking_slots: parking_slots_serializer.data
            }, 
            status=status.HTTP_200_OK
        )
