from django.db import models

# base information for every entry in the database to determine when things were added and updated
class BaseInfo(models.Model):
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False, blank=True, null=True)

    class Meta:
        ordering = ['-updated_at', '-created_at']
        abstract = True

class MallParking(BaseInfo):
    name = models.CharField(max_length=255)
    num_entries = models.IntegerField(default=3, blank=True) # cannot be less than 3
    flat_rate = models.DecimalField(default=40, blank=True, max_digits=19, decimal_places=10) # default is 40 pesos
    exceed_rate = models.DecimalField(default=5000, blank=True, max_digits=19, decimal_places=10) # default is 5000 pesos
    flatRate_duration = models.IntegerField(default=10800, blank=True) # default is 3 hours in milliseconds (3 * 60 * 60)
    exceed_duration = models.IntegerField(default=86400, blank=True) # default is 24 hours in milliseconds (24 * 60 * 60)
    return_duration = models.IntegerField(default=1800, blank=True) # default is 30 minutes in milliseconds (30 * 60)

    def __str__(self):
        return self.name

class Vehicle(BaseInfo):
    class VehicleType(models.TextChoices):
        S = 'S'
        M = 'M'
        L = 'L'
    plate_number = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=4, choices=VehicleType.choices)

    def __str__(self):
        return self.plate_number

# Parking slot size was created as a class to allow for other parking slot sizes to be added in the future
class ParkingSlotSize(BaseInfo):
    # id field is autogenerated, starts from 0
    name = models.CharField(max_length=255) # default values SP, MP, and LP, added sequentially on init to match the ids 0, 1 and 2
    continuous_rate = models.DecimalField(max_digits=19, decimal_places=10) # parking rate for this parking size
    # default values for the rate are:
    # 20 per hour for SP
    # 60 per hour for MP
    # 100 per hour for LP

    def __str__(self):
        return self.name

class ParkingSlot(BaseInfo):
    mall_parking = models.ForeignKey(MallParking, on_delete=models.CASCADE)
    parking_slot_size = models.ForeignKey(ParkingSlotSize, on_delete=models.CASCADE)
    distances = models.TextField() # array of integers in JSON format

class VehicleParking(BaseInfo):
    entry_datetime = models.DateTimeField(auto_now=False, auto_now_add=True)
    exit_datetime = models.DateTimeField(blank=True, null=True)
    is_flat_rate = models.BooleanField(default=True)
    parking_slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)