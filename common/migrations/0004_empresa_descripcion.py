# Generated by Django 2.1.7 on 2019-05-26 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_auto_20190525_0940'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresa',
            name='descripcion',
            field=models.TextField(blank=True, null=True),
        ),
    ]
