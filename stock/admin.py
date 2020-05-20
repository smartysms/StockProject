from django.contrib import admin
from django.contrib.admin import register, ModelAdmin
# Register your models here.
from . import models


@register(models.StockManagement)
class StockManagementAdmin(ModelAdmin):
    list_display = ('stock_Name', 'total_quantity',
                    'stock_price', 'last_Modified')


@register(models.UserStockHolding)
class UserHoldingAdmin(ModelAdmin):
    list_display = ['get_user_name', 'get_stock_name',
                    'occupied_quantity', 'lastModifiedOn']

    list_filter = ('user', 'stock')

    def get_stock_name(self, obj):
        return obj.stock.stock_Name

    def get_user_name(self, obj):
        return str(obj.user.first_name) + " "+str(obj.user.last_name)

    # def has_change_permission(self, request, obj=None):
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False


@register(models.UserPlaceTrade)
class UserPlaceTradeAdmin(ModelAdmin):
    list_display = ['get_user_name', 'get_stock_name',
                    'quantity', 'action', 'sale_type', 'price', 'status', 'createdOn']

    list_filter = ('status', 'action', 'sale_type', 'stock')

    def get_stock_name(self, obj):
        return obj.stock.stock_Name

    def get_user_name(self, obj):
        return str(obj.user.first_name) + " "+str(obj.user.last_name)


@register(models.TradeTransaction)
class TradeTransaction(ModelAdmin):
    list_display = ['get_seller_name', 'get_buyer_name',
                    'quantity', 'transaction_on']

    list_filter = ('seller_trade', 'buyer_trade')

    def get_seller_name(self, obj):
        return str(obj.seller_trade.first_name) + " " + str(obj.seller_trade.last_name)

    def get_buyer_name(self, obj):
        return str(obj.buyer_trade.first_name) + " "+str(obj.buyer_trade.last_name)
