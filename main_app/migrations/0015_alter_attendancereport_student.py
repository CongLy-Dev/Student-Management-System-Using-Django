# Generated by Django 4.1.3 on 2022-12-09 12:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0014_alter_leavereportstaff_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendancereport',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.student'),
        ),
    ]
