from django.db import transaction
import random

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from celery import shared_task, task, Task
from stock.models import UserStockHolding, UserPlaceTrade, TradeTransaction, StockManagement
from StockProject.constants import ORDER_STATUS, SALE_TYPE, USER_ACTION
from celery.schedules import crontab
import time
from datetime import datetime


class MyTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('<<<<<<<<<<<<<<<<{0!r} failed: {1!r}: >>>>>>>>>>>>>>>>>>>>'.format(
            task_id, exc))


@shared_task
def market_close():
    trade_obj = UserPlaceTrade.objects.filter(
        status__in=[ORDER_STATUS[1][0], ORDER_STATUS[4][0]], createdOn__date=datetime.now().date()).update(status=ORDER_STATUS[3][0])


@shared_task
def after_order_placed(t_id, u_id):
    with transaction.atomic():
        order_obj = UserPlaceTrade.objects.get(id=t_id, user_id=u_id)
        stock_obj = StockManagement.objects.get(id=order_obj.stock_id)
        if order_obj.action == USER_ACTION[0][0]:
            if order_obj.sale_type == 'bid':
                type_obj = UserPlaceTrade.objects.filter(
                    price__lte=order_obj.price, sale_type=SALE_TYPE[1][0], status__in=[ORDER_STATUS[4][0], ORDER_STATUS[1][0]]).exclude(user_id=order_obj.user_id)
            else:
                type_obj = UserPlaceTrade.objects.filter(sale_type=SALE_TYPE[1][0], status__in=[ORDER_STATUS[4][0], ORDER_STATUS[1][0]]).exclude(
                    user_id=order_obj.user_id).order_by('price')

            c_id = order_obj.user_id

        elif order_obj.action == USER_ACTION[1][0]:
            if order_obj.sale_type == SALE_TYPE[1][0]:
                type_obj = UserPlaceTrade.objects.filter(
                    price__gte=order_obj.price, sale_type=SALE_TYPE[2][0], status__in=[ORDER_STATUS[4][0], ORDER_STATUS[1][0]]).exclude(user_id=order_obj.user_id)

            else:
                type_obj = UserPlaceTrade.objects.filter(sale_type=SALE_TYPE[2][0], status__in=[ORDER_STATUS[1][0], ORDER_STATUS[4][0]]).exclude(
                    user_id=order_obj.user_id).order_by('-price')

            c_id = order_obj.user_id

        time.sleep(20)
        qty_fullfill = original_qty = order_obj.quantity
        cost = 0
        for obj in type_obj:
            if qty_fullfill:
                if obj.quantity <= qty_fullfill:
                    cost = (obj.quantity * obj.price) + cost
                    qty_fullfill = qty_fullfill - obj.quantity

                    update_user_holding_after_ask_bid(obj.stock_id, c_id, obj.id,
                                                      obj.user_id, obj.quantity, True)

                else:
                    cost = (qty_fullfill * obj.price) + cost
                    update_user_holding_after_ask_bid(obj.stock_id, c_id, obj.id,
                                                      obj.user_id, qty_fullfill, False)

                    qty_fullfill = 0
            else:
                break

        if qty_fullfill and cost:
            order_obj.quantity = qty_fullfill
            order_obj.status = ORDER_STATUS[4][0]
            stock_obj.set_stock_price(cost/(original_qty-qty_fullfill))
        elif qty_fullfill == 0:
            order_obj.status = ORDER_STATUS[0][0]
            order_obj.quantity = original_qty
            stock_obj.set_stock_price(cost/original_qty)

        order_obj.save()
        print("for loop completes")


@shared_task
def update_details_after_share_buy(trade_id, u_id):
    # This we are getting the object of trade palced this is for IPO
    print("Market function executed after the successfull")
    time.sleep(30)
    trade_obj = UserPlaceTrade.objects.get(id=trade_id, user_id=u_id)

    stock_obj = StockManagement.objects.get(id=trade_obj.stock_id)
    # creating stock entry in user account he is directly purchasing stock from market

    try:
        bid_hold_obj = UserStockHolding.objects.get(
            stock_id=trade_obj.stock_id, user_id=u_id)
        bid_hold_obj.occupied_quantity = bid_hold_obj.occupied_quantity + trade_obj.quantity
        bid_hold_obj.save()
    except Exception as e:
        bid_hold_obj = UserStockHolding.objects.create(
            stock_id=trade_obj.stock_id, occupied_quantity=trade_obj.quantity, user_id=u_id)

    # updating status in trade obj
    stock_obj.set_stock_after_buy(bid_hold_obj.occupied_quantity)
    trade_obj.status = ORDER_STATUS[0][0]
    trade_obj.save()

    print("Succesfully updated after buy from company")


# THis function is need to check with the both bid and ask simultaneously
def update_user_holding_after_ask_bid(stk_id, main_user_id, trade_id, current_user_id, qty, is_complete):
    try:
        # Get the bidder trade object here
        # this is to get the
        current_trade_obj = UserPlaceTrade.objects.get(
            id=trade_id, user_id=current_user_id)

        if current_trade_obj.sale_type == SALE_TYPE[1][0]:
            # get bid holding object
            bid_hold_obj = UserStockHolding.objects.filter(
                stock_id=stk_id, user_id=main_user_id).first()

            ask_hold_obj = UserStockHolding.objects.get(
                stock_id=stk_id, user_id=current_user_id)

            bid_user_id = main_user_id
            seller_user_id = current_user_id
        else:
            # get Bid holding object
            bid_hold_obj = UserStockHolding.objects.filter(
                stock_id=stk_id, user_id=current_user_id).first()

            ask_hold_obj = UserStockHolding.objects.get(
                stock_id=stk_id, user_id=main_user_id)

            bid_user_id = current_user_id
            seller_user_id = main_user_id

        # Check if bidder don't account for that stock
        if not bid_hold_obj:
            bid_hold_obj = UserStockHolding.objects.create(
                stock_id=stk_id, occupied_quantity=qty, user_id=bid_user_id)

        # If bidder has account for that stock means we need to add stock to his account
        # And need to remove stock from seller account
        elif bid_hold_obj:
            bid_hold_obj.occupied_quantity = bid_hold_obj.occupied_quantity + qty
            bid_hold_obj.save()
            print("Bidder holding successfully updated")

        ask_hold_obj.occupied_quantity = ask_hold_obj.occupied_quantity - qty
        ask_hold_obj.save()

        # update the transaction_details
        transaction_obj = TradeTransaction.objects.create(
            seller_trade_id=seller_user_id, buyer_trade_id=bid_user_id, quantity=qty, trade_id=current_trade_obj.id)

        if is_complete:
            current_trade_obj.status = ORDER_STATUS[0][0]
            current_trade_obj.save()
        else:
            current_trade_obj.status = ORDER_STATUS[4][0]
            current_trade_obj.quantity = current_trade_obj.quantity - qty
            current_trade_obj.save()

    except Exception as e:
        print("exception is E ", e)

    time.sleep(30)
    print("update successfull")
