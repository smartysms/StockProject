from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # For viewing content only this arte the views
    path("", views.IndexPage.as_view(), name="Website_Home"),

    path("login/", auth_views.LoginView.as_view(template_name='stock/login.html'), name="login"),

    path("logout/", views.LogoutView.as_view(), name="logout"),

    path("register/", views.RegisterUser.as_view(), name="register"),

    path("stock_trade/<int:id>", views.StockTradeView.as_view(), name="stock_trade"),

    path("order_detail/", views.OrderDetailView.as_view(), name="Order_details"),

    path("user_profile/<int:pk>/",
         views.UserPorfileView.as_view(), name="user_profile"),

    path("user_holding/",
         views.StockHoldingView.as_view(), name="stock_holding"),


    path("modify_order/<int:pk>/",
         views.ModifyOrderView.as_view(), name="modify_order"),

    path("order_cancel/<int:pk>/",
         views.order_cancel, name="Cancel_Order"),
    # This views are for the functionality

]
