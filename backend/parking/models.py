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
    flatRate_duration = models.IntegerField(default=10800, blank=True) # default is 3 hours in seconds (3 * 60 * 60)
    exceed_duration = models.IntegerField(default=86400, blank=True) # default is 24 hours in seconds (24 * 60 * 60)
    return_duration = models.IntegerField(default=1800, blank=True) # default is 30 minutes in seconds (30 * 60)

    def __str__(self):
        return self.name

class Vehicle(BaseInfo):
    class VehicleType(models.IntegerChoices):
        S = 0
        M = 1
        L = 2
    plate_number = models.CharField(max_length=255, primary_key=True)
    type = models.IntegerField(choices=VehicleType.choices)

    def __str__(self):
        return self.plate_number + " - " + str(self.type)

# Parking slot size was created as a class to allow for other parking slot sizes to be added in the future
class ParkingSlotSize(BaseInfo):
    name = models.CharField(max_length=255) # default values SP, MP, and LP
    value = models.IntegerField() # vehicle types with values less than or equal to this value can be parked on these slots
    continuous_rate = models.DecimalField(max_digits=19, decimal_places=10) # parking rate for this parking size
    # default values for the rate are:
    # 20 per hour for SP
    # 60 per hour for MP
    # 100 per hour for LP

    def __str__(self):
        return self.name + "(" + str(self.value) + ")"

class ParkingSlot(BaseInfo):
    mall_parking = models.ForeignKey(MallParking, on_delete=models.CASCADE)
    parking_slot_size = models.ForeignKey(ParkingSlotSize, on_delete=models.CASCADE)
    distances = models.TextField() # array of integers in JSON format
    vehicle_parking = models.ForeignKey('VehicleParking', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return str(self.pk) + " - " + self.parking_slot_size.__str__()

class VehicleParking(BaseInfo):
    entry_index = models.IntegerField() # index of the entry point
    entry_datetime = models.DateTimeField(auto_now=False, auto_now_add=True)
    exit_datetime = models.DateTimeField(blank=True, null=True)
    parking_slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    # checks if the starting rate is fixed rate or not
    @property
    def is_fixed_starting_rate(self):
        if self.exit_datetime is not None:
            # get the mall parking instance to see the threshold for a returning car
            mall_parking = MallParking.objects.get(id=self.parking_slot.mall_parking.pk)

            # get the latest vehicle parking instance from the same vehicle
            try:
                latest_parking = VehicleParking.objects.filter(vehicle__pk=self.vehicle.pk).exclude(pk=self.pk).latest('exit_datetime')

                # return False if the difference between the last parking and the current entry is less than the return duration threshold
                if latest_parking.exit_datetime.timestamp() - self.entry_datetime.timestamp() <= mall_parking.return_duration:
                    return False
            except VehicleParking.DoesNotExist:
                # handle the case where there is no pre-existing parking records
                return True
        # return True otherwise
        return True

    # computes the total charge for the parking, returns 0 if the vehicle has not exited yet.
    @property
    def total_charge(self):
        total_fee = 0
        if self.exit_datetime is not None:
            # get the mall parking instance to see the corresponding rates for the parking fee
            mall_parking = MallParking.objects.get(id=self.parking_slot.mall_parking.pk)
            
            # get the hourly rate from the parking slot depending on the size
            slot_rate = self.parking_slot.parking_slot_size.continuous_rate

            parking_duration = self.exit_datetime.timestamp() - self.entry_datetime.timestamp()
            if self.is_fixed_starting_rate:
                # compute the duration that is not covered by the fixed rate
                non_fixed_rate_duration = parking_duration - mall_parking.flatRate_duration

                # add the fixed rate to the total fee
                total_fee += mall_parking.flat_rate

                # handle the case when the duration exceeds the flat rate duration
                if non_fixed_rate_duration > 0:
                    # add the fee based on the continuous rate to be applied on a per second basis
                    total_fee += non_fixed_rate_duration * float(slot_rate) / (60 * 60)
            else:
                # add the fee based on the continuous rate to be applied on a per second basis
                total_fee += parking_duration * float(slot_rate) / (60 * 60)

        return total_fee