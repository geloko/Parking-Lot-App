from rest_framework import serializers
import json

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
        read_only_fields = ['plate_number']

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
        fields = ['id', 'entry_datetime', 'exit_datetime', 'is_flat_rate', 'parking_slot', 'vehicle']
        read_only_fields = ['id', 'entry_datetime', 'exit_datetime', 'is_flat_rate']

    def validate(self, data):
        # make sure that the instances exist in the database
        parking_slot = models.ParkingSlot.objects.get(id=data['parking_slot'].get['id'])
        vehicle = models.Vehicle.objects.get(id=data['plate_number'].get['plate_number'])

        data['parking_slot'] = parking_slot
        data['vehicle'] = vehicle

        # TODO: Validation of the entry and exit datetimes and the is_flat_rate attribute

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
