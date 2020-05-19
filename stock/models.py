from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from StockProject.constants import USER_ACTION, SALE_TYPE, GENDER_TYPE, ORDER_STATUS
# Create your models here.


class StockManagement(models.Model):
    stock_Name = models.CharField(max_length=50)
    total_quantity = models.IntegerField()
    stock_price = models.DecimalField(max_digits=6, decimal_places=2)
    last_Modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stockmanagement'
        verbose_name_plural = 'StocksManagement'

    def __str__(self):
        return self.stock_Name

    def get_stock_price(self):
        return self.stock_price

    def set_stock_price(self, new_price):
        self.stock_price = new_price
        self.save()

    def set_stock_after_buy(self, new_qty):
        self.total_quantity = self.total_quantity - new_qty
        self.save()


class UserStockHolding(models.Model):
    def __init__(self, *args, **kwargs):
        super(UserStockHolding, self).__init__(*args, **kwargs)

    stock = models.ForeignKey(StockManagement, on_delete=models.CASCADE)
    occupied_quantity = models.IntegerField()
    lastModifiedOn = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'userstockholding'
        verbose_name_plural = 'UserStockHolding'

    def __str__(self):
        return self.user.username


class UserPlaceTrade(models.Model):
    def __init__(self, *args, **kwargs):
        super(UserPlaceTrade, self).__init__(*args, **kwargs)
    stock = models.ForeignKey(StockManagement, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    # We can also use unix time field for more accurate time stamp
    createdOn = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=USER_ACTION, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    sale_type = models.CharField(
        max_length=100, choices=SALE_TYPE, default=SALE_TYPE[0][0])

    status = models.CharField(
        max_length=50, choices=ORDER_STATUS, default=ORDER_STATUS[1][0])

    class Meta:
        db_table = 'userplacetrade'
        ordering = ['-price', 'createdOn']
        verbose_name_plural = 'UserPlaceTrade'

    def __str__(self):
        return self.user.first_name


class TradeTransaction(models.Model):
    seller_trade = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='seller_id')
    buyer_trade = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='buyer_trade')
    trade = models.ForeignKey(
        UserPlaceTrade, on_delete=models.DO_NOTHING, null=True)
    quantity = models.IntegerField(default=0)
    transaction_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tradetransaction'
        verbose_name_plural = 'TradeTransaction'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(
        validators=[MaxValueValidator(100), MinValueValidator(1)], null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_TYPE, blank=True)

    class Meta:
        db_table = 'profile'
        verbose_name_plural = 'Profile'

    def __str__(self):
        return self.user.first_name


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
