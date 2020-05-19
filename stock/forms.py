from django import forms

from StockProject.constants import USER_ACTION, SALE_TYPE, GENDER_TYPE
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import InlineRadios
from .models import StockManagement, Profile, UserPlaceTrade, UserStockHolding
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from crispy_forms.layout import Submit


class HorizontalRadioSelect(forms.RadioSelect):
    template_name = 'stock/horizontal_select.html'


class UserTradeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.s_type = kwargs.pop('stock_type', None)
        self.price_val = kwargs.pop('price_value', None)
        self.u_id = kwargs.pop('u_id', None)
        super(UserTradeForm, self).__init__(*args, **kwargs)

        self.fields['stock'] = forms.ModelChoiceField(
            queryset=StockManagement.objects.filter(id=self.s_type))
        self.helper = FormHelper(self)
        self.helper[3] = InlineRadios('sale_type')
        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn-primary'))

    class Meta:
        model = UserPlaceTrade
        fields = ['stock', 'quantity', 'action', 'sale_type', 'price']

    def clean(self):
        cleaned_data = super(UserTradeForm, self).clean()
        qty = cleaned_data.get('quantity')
        action_item = cleaned_data.get('action')
        sale_type = cleaned_data.get('sale_type', None)

        if not sale_type:
            raise forms.ValidationError(
                {'sale_type': ["This field is required", ]})

        if sale_type.lower() == SALE_TYPE[0][0] or sale_type.lower() == SALE_TYPE[3][0]:
            cleaned_data['price'] = self.price_val

        # If user wwant to sell the stock
        if action_item.lower() == USER_ACTION[1][0]:

            holding_object = UserStockHolding.objects.get(
                stock=cleaned_data.get('stock'), user_id=self.u_id)

            if holding_object.occupied_quantity < qty:
                raise forms.ValidationError(
                    {'quantity': ["You don't have enough share to sell kindly check the stock quantity you have", ]})

        return cleaned_data


class TradeModifyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):

        super(TradeModifyForm, self).__init__(*args, **kwargs)

    class Meta:
        model = UserPlaceTrade
        fields = ['action', 'quantity', 'price']


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):

        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper[1] = InlineRadios('gender')
        self.fields['gender'] = forms.ChoiceField(
            choices=GENDER_TYPE, widget=forms.RadioSelect())

        self.helper.add_input(
            Submit('submit', 'Submit', css_class='btn-primary'))
        self.helper.form_tag = False

    class Meta:
        model = Profile
        fields = ['age', 'gender']


class UserDetailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserDetailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
