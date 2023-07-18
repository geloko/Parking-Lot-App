# Generated by Django 4.2.3 on 2023-07-17 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('parking', '0002_vehicleparking_entry_index'), ('parking', '0003_remove_vehicleparking_is_flat_rate'), ('parking', '0004_alter_vehicle_plate_number'), ('parking', '0005_parkingslotsize_value_alter_vehicle_type'), ('parking', '0006_alter_vehicle_type')]

    dependencies = [
        ('parking', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicleparking',
            name='entry_index',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='vehicleparking',
            name='is_flat_rate',
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='plate_number',
            field=models.CharField(max_length=255, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='parkingslotsize',
            name='value',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='type',
            field=models.CharField(choices=[(0, 'S'), (1, 'M'), (2, 'L')], max_length=4),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='type',
            field=models.IntegerField(choices=[(0, 'S'), (1, 'M'), (2, 'L')]),
        ),
    ]
