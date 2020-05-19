# Generated by Django 3.0.5 on 2020-05-12 08:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StockManagement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_Name', models.CharField(max_length=50)),
                ('total_quantity', models.IntegerField()),
                ('stock_price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('last_Modified', models.DateTimeField(auto_now=True)),
                ('available_quantity', models.IntegerField()),
            ],
            options={
                'verbose_name_plural': 'StocksManagement',
                'db_table': 'stockmanagement',
            },
        ),
        migrations.CreateModel(
            name='UserStockHolding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('occupied_quantity', models.IntegerField()),
                ('lastModifiedOn', models.DateTimeField(auto_now=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stock.StockManagement')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'UserStockHolding',
                'db_table': 'userstockholding',
            },
        ),
        migrations.CreateModel(
            name='UserPlaceTrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('createdOn', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(choices=[('buy', 'BUY'), ('sell', 'SELL')], max_length=10)),
                ('sale_type', models.CharField(choices=[('market_order', 'MARKET ORDER'), ('ask', 'ASK'), ('bid', 'BID')], default='MARKET ORDER', max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('status', models.CharField(choices=[('complete', 'COMPLETE'), ('pending', 'PENDING'), ('cancel', 'CANCEL')], max_length=50)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stock.StockManagement')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'UserPlaceTrade',
                'db_table': 'userplacetrade',
            },
        ),
        migrations.CreateModel(
            name='TradeTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_trade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_trade', to=settings.AUTH_USER_MODEL)),
                ('seller_trade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seller_id', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'TradeTransaction',
                'db_table': 'tradetransaction',
            },
        ),
    ]
