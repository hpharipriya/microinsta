# Generated by Django 3.1.2 on 2020-10-26 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insta', '0006_auto_20201026_1343'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='continent',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='location',
            name='country',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='location',
            name='county',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='location',
            name='postcode',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AddField(
            model_name='location',
            name='state',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='location',
            name='country_code',
            field=models.CharField(default='', max_length=5),
        ),
    ]
