# Generated by Django 3.1.7 on 2021-03-17 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_auto_20210317_2117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='park',
            name='Actual_Depart_Date_Time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
