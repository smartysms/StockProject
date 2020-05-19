# Generated by Django 3.0.5 on 2020-05-15 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0008_auto_20200515_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userplacetrade',
            name='status',
            field=models.CharField(choices=[('complete', 'COMPLETE'), ('pending', 'PENDING'), ('cancel', 'CANCEL'), ('timeout', 'TIMEOUT'), ('patial', 'PARTIAL')], default='pending', max_length=50),
        ),
    ]
