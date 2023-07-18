from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from rest_framework import viewsets, mixins, status, generics
from rest_framework.response import Response

from . import models
from . import serializers

# Base view set for table attributes containing the create, read and update actions but not delete.
class BaseViewSet(viewsets.GenericViewSet, 
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin
):
    def perform_create(self, serializer): 
        if serializer.is_valid():
            content = serializer.save()
            return Response(content, status=status.HTTP_201_CREATED)
        else:
            content = serializer.errors
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

class MallParkingViewSet(
    viewsets.GenericViewSet, 
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    queryset = models.MallParking.objects.all()
    serializer_class = serializers.MallParkingSerializer

class VehicleViewSet(
    viewsets.GenericViewSet, 
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    queryset = models.Vehicle.objects.all()
    serializer_class = serializers.VehicleSerializer

class ParkingSlotSizeViewSet(BaseViewSet):
    queryset = models.ParkingSlotSize.objects.all()
    serializer_class = serializers.ParkingSlotSizeSerializer

class ParkingSlotViewSet(BaseViewSet):
    queryset = models.ParkingSlot.objects.all()
    serializer_class = serializers.ParkingSlotSerializer

@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_description="""Unpark function for the application. 
    This takes in the plate number of the vehicle, and if the vehicle is parked inside any parking slot in the database, this vehicle would then exit 
    the parking space and get charge with its respective parking fees.""",
))
class VehicleParkingViewSet(viewsets.GenericViewSet, 
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin
):
    queryset = models.VehicleParking.objects.all()
    serializer_class = serializers.VehicleParkingSerializer

    def update(self, request, *args, **kwargs):
        # Get the parking slot for the vehicle. We expect there to be only one parking slot containing the vehicle.
        parking_slot_queryset = models.ParkingSlot.objects.filter(vehicle_parking__vehicle__pk=request.data['plate_number'])
        if not(parking_slot_queryset.exists()):
            return Response("Unknown plate number.", status=status.HTTP_400_BAD_REQUEST)
        parking_slot = parking_slot_queryset.get()
        vehicle_parking = parking_slot.vehicle_parking

        serializer = self.serializer_class(instance=vehicle_parking, data=request.data)
        if serializer.is_valid():
            content = serializer.save()
            return Response(content, status=status.HTTP_200_OK)
        else:
            content = serializer.errors
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

# viewset for entering vehicles and parking slot assignment
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_description="""Park function for the application. 
    This takes in the entry index to denote which entrance the vehicle entered in, along with the vehicle details: the plate number and the vehicle size/type. 
    The parking is assigned based on the nearest possible slot and then when there are slots with similar distances from the entrance, we prioritize 
    slots that are smaller and are better fit for the vehicle.""",
))
class VehicleParkingEntryViewSet(viewsets.GenericViewSet, 
    mixins.CreateModelMixin,
):
    queryset = models.VehicleParking.objects.all()
    serializer_class = serializers.VehicleParkingEntrySerializer

@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_description="""Mall creation function. It allows the user to initialize the configuration of the mall with its name, number of entrances and its parkings slots. 
    It is also possible to customize the parking rates and the duration on which different rates apply.""",
))
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
