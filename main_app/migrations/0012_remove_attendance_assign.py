# Generated by Django 4.1.3 on 2022-12-09 11:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0011_remove_leavereportstudent_assign'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='assign',
        ),
    ]