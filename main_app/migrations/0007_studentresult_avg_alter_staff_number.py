# Generated by Django 4.1.3 on 2022-12-08 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0006_remove_attendance_assign_attendance_assign'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentresult',
            name='avg',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='staff',
            name='number',
            field=models.CharField(max_length=15, null=True),
        ),
    ]