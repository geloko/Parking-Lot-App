from rest_framework import serializers
import json

# we use the rest framework for our frontend and backend communications

import models

class MallParkingSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.MallParking
    fields = ['id', 'num_entries', 'flat_rate', 'exceed_rate', 'flatRate_duration', 'exceed_duration', 'return_duration']
    read_only_fields = ['id']

  def validate(self, data):
    if(data['num_entries'] < 3):
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
    child=serializers.IntegerField(min_value=0),
    min_length=3 # minimum number entries is 3, therefore the number of distances must be greater than 3
  )
  class Meta:
    model = models.ParkingSlot
    fields = ['id', 'mall_parking', 'parking_slot_size', 'distances']
    read_only_fields = ['id']

  def validate(self, data):
    mall_parking = models.MallParking.objects.get(id=data['mall_parking'].get['id'])
    parking_slot_size = models.ParkingSlotSize.objects.get(id=data['parking_slot_size'].get['id'])

    # make sure that the number of distance inputs match the number of mall entries
    if(len(data['distances']) != mall_parking.num_entries):
      raise serializers.ValidationError('The number of distances must match the number of entries in the mall.')
    distances_json = json.dumps(data['distances'])

    data['distances'] = distances_json
    data['mall_parking'] = mall_parking
    data['parking_slot_size'] = parking_slot_size
    return data

class VehicleParkingSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.VehicleParking
    fields = ['id', 'entry_datetime', 'exit_datetime', 'is_flat_rate', 'parking_slot', 'vehicle']
    read_only_fields = ['id', 'entry_datetime', 'exit_datetime', 'is_flat_rate']