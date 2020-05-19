# Generated by Django 3.0.5 on 2020-05-18 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0010_auto_20200519_0141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userplacetrade',
            name='status',
            field=models.CharField(choices=[('complete', 'COMPLETE'), ('pending', 'PENDING'), ('cancel', 'CANCEL'), ('timeout', 'TIMEOUT'), ('partial', 'PARTIAL')], default='pending', max_length=50),
        ),
    ]
