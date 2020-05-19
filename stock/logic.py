from StockProject.constants import ORDER_STATUS, SALE_TYPE
from stock.models import UserPlaceTrade, StockManagement, UserStockHolding, TradeTransaction

operation_obj = UserPlaceTrade.objects.get(id=41, user_id=18)

if operation_obj.sale_type == 'ask':
    sale_type = 'bid'

elif operation_obj.sale_type == 'bid':
    sale_type = 'ask'

type_obj = UserPlaceTrade.objects.filter(
    price=sale_type.price, sale_type=sale_type, status='pending')

print("type of is ", type_obj)
qty_fullfill = operation_obj.quantity
cost = 0
for obj in type_obj:
    if qty_fullfill:
        if obj.quantity <= qty_fullfill:
            cost = (obj.quantity * obj.price) + cost
            qty_fullfill = qty_fullfill - obj.quantity
            print("cost in if ", cost, " aty ", qty_fullfill)
        else:
            qty_fullfill = obj.quantity - qty_fullfill
            cost = (obj.quantity * obj.price) + cost
            print("cost in if ", cost, " aty ", qty_fullfill)
