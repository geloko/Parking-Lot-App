from django.contrib import admin

from . import models

admin.site.register(models.MallParking)
admin.site.register(models.Vehicle)
admin.site.register(models.ParkingSlotSize)
admin.site.register(models.VehicleParking)

@admin.register(models.ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'parking_slot_size', 'distances')