# Generated by Django 2.2.4 on 2020-02-10 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('handler', '0003_clicksinfo_cpi'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clicksinfo',
            name='cpi',
            field=models.CharField(default='0', max_length=50),
        ),
        migrations.AlterField(
            model_name='clicksinfo',
            name='date',
            field=models.CharField(max_length=23),
        ),
    ]
