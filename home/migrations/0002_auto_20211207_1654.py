# Generated by Django 3.2.8 on 2021-12-07 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lotrinh',
            name='CapBen',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='lotrinh',
            name='XuatBen',
            field=models.TimeField(),
        ),
    ]
