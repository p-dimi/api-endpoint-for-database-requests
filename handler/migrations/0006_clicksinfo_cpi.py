# Generated by Django 2.2.4 on 2020-02-11 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('handler', '0005_auto_20200211_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='clicksinfo',
            name='cpi',
            field=models.CharField(default='0', max_length=50),
        ),
    ]
