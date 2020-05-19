from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
import os
import sys
import json
import random
from django.urls import reverse
from datetime import datetime, date, timedelta
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# from django.core.wsgi
from django.views.generic import CreateView, UpdateView, FormView
from django.contrib.auth.forms import UserCreationForm
from django.views import View
from django.views.generic.base import TemplateView
from django.conf import settings
from .models import StockManagement, UserPlaceTrade, Profile, UserStockHolding, TradeTransaction
from .forms import UserTradeForm, ProfileForm, UserDetailForm, TradeModifyForm
from stock.decorators import check_market_time
from .tasks import after_order_placed, update_details_after_share_buy
from django.contrib import messages
from StockProject.constants import ORDER_STATUS, USER_ACTION, SALE_TYPE
from django.db.models import Sum
from .utilities import convert_to_localtime


@method_decorator(login_required, name="dispatch")
class IndexPage(TemplateView):
    template_name = 'stock/index.html'

    def __init__(self, **kwargs):
        super(IndexPage, self).__init__(**kwargs)

        self.send_data = []

    def get_context_data(self, **kwargs):
        context = super(IndexPage, self).get_context_data(**kwargs)
        queryset = StockManagement.objects.all()
        for obj in queryset:
            date_time = convert_to_localtime(obj.last_Modified)

            self.send_data.append([obj.id, str(obj.stock_Name), str(
                obj.total_quantity), str(obj.stock_price), str(date_time), ""])
        context['stock_data'] = json.dumps(self.send_data)
        return context


class RegisterUser(View):
    form_class = UserCreationForm
    template_name = 'stock/register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            new_obj = User.objects.get(id=form.instance.id)
            self.log_user_in(request, form)
            return HttpResponseRedirect('/')
        return render(request, self.template_name, {'form': form})

    def log_user_in(self, request, form):
        user = authenticate(username=form.cleaned_data.get(
            'username'), password=form.cleaned_data.get('password1'))
        if user is not None:
            return auth_login(request, user)


class LogoutView(View):
    def get(self, request):
        auth_logout(request)
        return HttpResponseRedirect(reverse(settings.LOGIN_URL))


@method_decorator(check_market_time, name='dispatch')
@method_decorator(login_required, name='dispatch')
class StockTradeView(CreateView):
    model = UserPlaceTrade
    form_class = UserTradeForm
    price_data = 0
    stk_id = None
    u_id = None
    template_name = 'stock/stock_trade.html'
    success_url = "Website_Home"

    def get_context_data(self, **kwargs):
        ctx = super(StockTradeView, self).get_context_data(**kwargs)
        ctx['d_price'] = self.price_data
        try:
            stock_obj = UserStockHolding.objects.get(
                user=self.request.user, stock_id=self.stk_id)
            ctx['sell_applicable'] = True
        except Exception as e:
            ctx['sell_applicable'] = False

        return ctx

    def get_form_kwargs(self):
        kwargs = super(StockTradeView, self).get_form_kwargs()
        kwargs['stock_type'] = self.stk_id = self.kwargs.get('id')
        kwargs['price_value'] = self.price_data = StockManagement.objects.get(
            id=kwargs['stock_type']).stock_price
        kwargs['u_id'] = self.u_id = self.request.user.id

        return kwargs

    def form_valid(self, form):
        trade_obj = form.save(commit=False)
        trade_obj.user_id = self.request.user.id
        trade_obj.save()
        messages.success(self.request, 'Your order placed successfully')
        if trade_obj.action == USER_ACTION[2][0]:
            update_details_after_share_buy.delay(
                trade_obj.id, trade_obj.user_id)

        else:
            after_order_placed.delay(trade_obj.id, trade_obj.user_id)
        return HttpResponseRedirect(reverse(self.success_url))


@method_decorator(login_required, name='dispatch')
class OrderDetailView(TemplateView):
    template_name = 'stock/order_detail.html'

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)

        history_data = []
        pending_data = []
        history_order = UserPlaceTrade.objects.filter(
            user=self.request.user).exclude(status=ORDER_STATUS[1][0]).order_by('-createdOn')

        pending_order = UserPlaceTrade.objects.filter(
            user=self.request.user, status__in=[ORDER_STATUS[1][0], ORDER_STATUS[4][0]]).order_by('-createdOn')

        for obj in history_order:
            created = convert_to_localtime(obj.createdOn)
            if TradeTransaction.objects.filter(trade_id=obj.id).exists():
                quantity = TradeTransaction.objects.filter(
                    trade_id=obj.id).aggregate(Sum('quantity'))

                qty = str(quantity['quantity__sum'])
                status = 'complete'
            else:
                qty = str(obj.quantity)
                status = str(obj.status)

            history_data.append([str(obj.stock.stock_Name), str(qty), str(obj.action), str(
                obj.sale_type), str(obj.price), status, str(created)])

        for obj in pending_order:
            created = convert_to_localtime(obj.createdOn)
            pending_data.append([str(obj.id), str(obj.stock.stock_Name), str(
                obj.quantity), str(obj.action), str(obj.sale_type), str(obj.price), str(obj.status), str(created)])

        context['history_order'] = json.dumps(history_data)
        context['pending_order'] = json.dumps(pending_data)

        return context


@method_decorator(login_required, name="dispatch")
class UserPorfileView(UpdateView):
    model = User
    form_class = UserDetailForm
    profile_form_class = ProfileForm
    template_name = 'stock/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super(UserPorfileView, self).get_context_data(**kwargs)

        if 'user_form' not in context:
            context['user_form'] = self.form_class(
                self.request.GET, instance=self.request.user)
        if 'profile_form' not in context:
            context['profile_form'] = self.profile_form_class(
                self.request.GET, instance=self.request.user.profile)

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email
        }
        profile_initial = {
            'age': request.user.profile.age,
            'gender': request.user.profile.gender
        }
        user_form = self.form_class(initial=user_initial)
        profile_form = self.profile_form_class(initial=profile_initial)

        return render(request, self.template_name, {'user_form': user_form, 'profile_form': profile_form})

    def post(self, request, *args, **kwargs):
        user_form = self.form_class(
            self.request.POST, instance=request.user)

        profile_form = self.profile_form_class(
            self.request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, (
                'Your profile was successfully updated!'))

        return render(request, self.template_name, {'user_form': user_form, 'profile_form': profile_form})


@method_decorator(login_required, name='dispatch')
class StockHoldingView(TemplateView):
    template_name = 'stock/my_stock_holding.html'

    def get_context_data(self, **kwargs):
        context = super(StockHoldingView, self).get_context_data(**kwargs)

        holding_data = []

        holding_order = UserStockHolding.objects.filter(user=self.request.user)

        for obj in holding_order:
            l_update = convert_to_localtime(obj.lastModifiedOn)
            holding_data.append([str(obj.stock.stock_Name), str(
                obj.occupied_quantity), str(l_update)])

        context['stock_holding'] = json.dumps(holding_data)

        return context


@method_decorator(login_required, name='dispatch')
class ModifyOrderView(UpdateView):
    template_name = 'stock/modify_order.html'
    form_class = TradeModifyForm
    model = UserPlaceTrade

    success_url = 'Order_details'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        trade_form = self.form_class(self.request.POST, instance=self.object)
        if trade_form.is_valid():
            stock_obj = UserStockHolding.objects.get(
                user=request.user, stock_id=self.object.stock_id)
            if trade_form.cleaned_data.get('action') == USER_ACTION[1][0] and stock_obj.occupied_quantity < trade_form.cleaned_data.get('quantity'):
                trade_form.add_error(
                    'quantity', 'Please enter a valid quantity share quantity')
                return self.form_invalid(trade_form)
            trade_form.save()

            messages.success(self.request, 'Your order modified successfully')
            if self.object.action == USER_ACTION[2][0]:
                update_details_after_share_buy.delay(
                    trade.id, trade.user_id)

            else:

                after_order_placed.delay(self.object.id, self.object.user_id)

            return HttpResponseRedirect(reverse(self.success_url))
        else:
            return render(request, self.template_name, {'form': trade_form, })


def order_cancel(request, pk):
    trade_obj = UserPlaceTrade.objects.get(id=pk)
    trade_obj.status = ORDER_STATUS[2][0]
    trade_obj.save()

    messages.success(request, ('Your order canceled successfully!'))

    return HttpResponseRedirect(reverse('Order_details'))
