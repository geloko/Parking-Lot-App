from django.contrib import admin

from . import models

admin.site.register(models.MallParking)
admin.site.register(models.Vehicle)
admin.site.register(models.ParkingSlotSize)
admin.site.register(models.ParkingSlot)
admin.site.register(models.VehicleParking)