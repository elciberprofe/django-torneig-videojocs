# Generated by Django 5.2.1 on 2025-06-08 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competicions', '0003_torneig_equips'),
    ]

    operations = [
        migrations.AddField(
            model_name='jugador',
            name='dorsal',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='jugador',
            name='posicio',
            field=models.CharField(default='Mixt', max_length=50),
        ),
    ]
