from rest_framework import serializers
import json
from django.db.models import Subquery

# we use the rest framework for our frontend and backend communications

from . import models

class MallParkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MallParking
        fields = ['id', 'name', 'num_entries', 'flat_rate', 'exceed_rate', 'flatRate_duration', 'exceed_duration', 'return_duration']
        read_only_fields = ['id']

    def validate(self, data):
        if(data.__contains__('num_entries') and data['num_entries'] < 3):
            raise serializers.ValidationError('The number of entries cannot be less than 3.')
        return data

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Vehicle
        fields = ['plate_number', 'type']

# added to account for new sizes in the future
class ParkingSlotSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ParkingSlotSize
        fields = ['id', 'name', 'continuous_rate']
        read_only_fields = ['id']

class ParkingSlotSerializer(serializers.ModelSerializer):
    mall_parking = MallParkingSerializer()
    parking_slot_size = ParkingSlotSizeSerializer()
    distances = serializers.ListField(
        child = serializers.IntegerField(min_value=0),
        min_length = 3, # minimum number entries is 3, therefore the number of distances must be greater than 3
        write_only=True
    )
    class Meta:
        model = models.ParkingSlot
        fields = ['id', 'mall_parking', 'parking_slot_size', 'distances']
        read_only_fields = ['id']

    def validate(self, data):
        # make sure that the instances exist in the database
        mall_parking = models.MallParking.objects.get(id=data['mall_parking'].get['id'])
        parking_slot_size = models.ParkingSlotSize.objects.get(id=data['parking_slot_size'].get['id'])

        data['mall_parking'] = mall_parking
        data['parking_slot_size'] = parking_slot_size

        # make sure that the number of distance inputs match the number of mall entries
        if(len(data['distances']) != mall_parking.num_entries):
            raise serializers.ValidationError('The number of distances must match the number of entries in the mall.')
        
        # save the integer array for distances as a string in JSON format
        distances_json = json.dumps(data['distances'])
        data['distances'] = distances_json

        return data

class VehicleParkingSerializer(serializers.ModelSerializer):
    parking_slot = ParkingSlotSerializer()
    vehicle = VehicleSerializer()
    class Meta:
        model = models.VehicleParking
        fields = ['id', 'entry_datetime', 'exit_datetime', 'parking_slot', 'vehicle', 'is_fixed_starting_rate', 'total_charge']
        read_only_fields = ['id', 'is_fixed_starting_rate', 'total_charge']

    def validate(self, data):
        # make sure that the instances exist in the database
        parking_slot = models.ParkingSlot.objects.get(id=data['parking_slot'].get['id'])
        vehicle = models.Vehicle.objects.get(id=data['vehicle'].get['plate_number'])

        data['parking_slot'] = parking_slot
        data['vehicle'] = vehicle

        # check if the exit datetime is after the entry datetime
        if data['exit_datetime'] is not None and data['entry_datetime'] > data['exit_datetime']:
            raise serializers.ValidationError('The exit datetime cannot be before the exit datetime.')

        return data

# special serializer for assigning a parking slot to vehicles
class VehicleParkingEntrySerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer()
    class Meta:
        model = models.VehicleParking
        fields = ['id', 'entry_index', 'entry_datetime', 'vehicle']
        read_only_fields = ['id']

    def validate(self, data):
        # make sure that the instances exist in the database
        vehicle = models.Vehicle(
            plate_number=data['vehicle']['plate_number'],
            type=data['vehicle']['type']
        )

        entry_index = data['entry_index']
        """
        Get all the empty parking slots
        """
        # Get the vehicle parking instances occupied parking slots. Null exit datetime indicate occupied.
        occupied_parking_slot_ids = models.VehicleParking.objects.filter(exit_datetime=None).values('parking_slot_id')
        valid_parking_slots = models.ParkingSlot.objects.filter(parking_slot_size__value__gte=data['vehicle']['type'])
        free_parking_slots = valid_parking_slots.exclude(id__in=Subquery(occupied_parking_slot_ids))
        
        # Querying the empty parking slots like this is computationally expensive. 
        # An alternative that I have thought of is to have an is_occupied attribute in the ParkingSlot.
        # However, it is also not fool proof because that might cause inconsistencies in the data if not updated properly, like if an admin modifies it without using the API.
        # My take is that we could start with a computationally expensive but reliable solution and only switch to an efficient one when necessary.

        # use the first free parking slot as the initial value
        parking_slot = free_parking_slots.first()

        if parking_slot is None:
            raise serializers.ValidationError('No available parking slots.')

        min_distance = json.loads(parking_slot.distances)[entry_index]
        for free_parking_slot in free_parking_slots:
            # distances array is saved as a string in json format
            distances_arr = json.loads(free_parking_slot.distances)

            # set the minimum as the new parking slot and update the current minimum distance
            if min_distance > distances_arr[entry_index]:
                parking_slot = free_parking_slot
                min_distance = json.loads(parking_slot.distances)[entry_index]

        data['parking_slot'] = parking_slot
        data['vehicle'] = vehicle

        return data

    def save(self):
        vehicle_data = self.validated_data['vehicle']
        vehicle = models.Vehicle(
            plate_number = vehicle_data.plate_number,
            type = vehicle_data.type
        )

        if vehicle.DoesNotExist:
            vehicle.save()

        vehicle_parking = models.VehicleParking(
            entry_index = self.validated_data['entry_index'],
            parking_slot = self.validated_data['parking_slot'],
            vehicle = vehicle
        )

        vehicle_parking.save()

        return {
            "vehicle_parking": vehicle_parking,
            "message": "The vehicle has been parked."
        }

        

class MallParkingSlotsSerializer(serializers.Serializer):
    mall_parking = MallParkingSerializer()
    parking_slots = ParkingSlotSerializer(read_only=True, many=True)
    parking_slot_distance_list = serializers.ListField(
        child = serializers.ListField(
            child = serializers.IntegerField(min_value=0),
            min_length = 3 # minimum number entries is 3, therefore the number of distances must be greater than 3
        ),
        write_only=True
    )
    parking_slot_size_list = serializers.ListField(
        child = serializers.IntegerField(),
        write_only=True
    )

    def validate(self, data):
        # check that the parking slot lists have the same size
        if(len(data['parking_slot_distance_list']) != len(data['parking_slot_size_list'])):
            raise serializers.ValidationError('The lists must have the same length.')

        mall_parking = models.MallParking(**data['mall_parking'])
        data['mall_parking'] = mall_parking

        parking_slots = []
        for i in range(0, len(data['parking_slot_distance_list'])):
            # check that the number of distance matches the number of entries in the mall
            if len(data['parking_slot_distance_list'][i]) != mall_parking.num_entries:
                raise serializers.ValidationError('Invalid parking slot distances input.')
            
            parking_slot_size = models.ParkingSlotSize.objects.get(id=data['parking_slot_size_list'][i])
            parking_slot_instance = models.ParkingSlot(
                mall_parking = mall_parking,
                parking_slot_size = parking_slot_size,
                distances = data['parking_slot_distance_list'][i]
            )
            parking_slots.append(parking_slot_instance)
        data['parking_slots'] = parking_slots

        return data

    def save(self):
        mall_parking = self.validated_data['mall_parking']
        mall_parking.save()

        for i in range(0, len(self.validated_data['parking_slots'])):
            self.validated_data['parking_slots'][i].save()

        return True
