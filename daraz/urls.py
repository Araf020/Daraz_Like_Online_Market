
from django.contrib import admin
from django.urls import path, include
from . import views
from .checkout import checkout
from .LoginAndLogout import loginOrSignup
from .Sales import sale
from .order import ordertrack


urlpatterns = [
    path('',views.Index.as_view(), name = 'homepage'),
    path('sell/',views.sell),
    path('sell/sellsignup/', sale.sellsignup, name='sale_signup'),
    path('sell/saleLogin/', sale.selllogin, name='sale_login'),
    path('info/',views.list_jobs, name='test'),
    path('home/signup/', loginOrSignup.signup, name='signup'),
    path('login/', loginOrSignup.user_login, name='login'),
    path('home/', views.products, name='home'),
    # path('sell/',views.sell),
    path('home/logout/', loginOrSignup.user_logout, name='logout'),
    path('home/forget_pass/', loginOrSignup.forgetPass, name='forget_pass'),
    path('home/verify_mail/', loginOrSignup.verifymail, name='verify_mail'),
    path('home/reset_pass/', loginOrSignup.resetpass, name='reset_pass'),

    path('home/sell/', views.sell, name='sell'),
    path('home/login/', loginOrSignup.user_login),
    path('home/sell/sellsignup/', sale.sellsignup),
    path('home/sell/sellsignup/saleLogin/', sale.selllogin),
    path('saleLogout/',sale.saleLogout),
    path('home/sell/saleLogin/', sale.selllogin),
    # path('home/sell/saleLogin/saleLogin/sellsignup/', views.sellsignup),
    # path('home/sell/sellsignup/saleLogin/saleLogin/sellsignup/',views.sellsignup),
    # path('home/sell/sellsignup/saleLogin/saleLogin/sellsignup/saleLogin/',views.selllogin),
    path('saleLogin/',sale.selllogin),
    # path('saleLogin/saleLogin/sellsignup/',sale.sellsignup),
    # path('login/home/',views.products),
    path('login/profile/', views.profile),
    path('saleproduct/', sale.sale),
    # path('home/login/home/',loginOrSignup.user_login, name='login'),
    path('home/profile/',views.profile, name='profile'),
    # path('home/order/',views.order, name = 'order'),
    path('home/cart/',views.cart,name = 'cart'),

    path('home/pay_card/',checkout.credit_check, name= 'checkout'),
    # path('home/creditpay/',checkout.credit_check, name= 'checkout'),
    # path('home/place_your_order',views.products),
    path('home/shipment/',checkout.shipment),
    path('home/profile/accountsettings/',views.accountsettings),
    path('home/<int:catid>/',views.showCat_wise),
    path('home/track/',views.trackYourorder,name='track'),
    path('home/payment/',views.paymentChoice, name='payment_choice'),
    path('test/',views.test),
    path('home/pay_bkash/',checkout.bkash_check, name = 'bkash'),
    path('home/verify_bkash/',checkout.verify_bkash, name = 'v_b'),
    path('home/confirm_bkash_pay/',checkout.verify_pin, name = 'v_p'),

    # path('home/pay_card/',checkout.credit_check, name = 'credit'),
    path('home/place_your_order/',checkout.place_your_order , name = 'order_place'),
    path('home/buy/',views.buy, name = 'buy'),
    # path('home/order_confirmation/',checkout.order_confirmation, name = 'order_confirmation'),
    path('home/my_orders',ordertrack.orderlist, name = 'my_orders'),
    path('home/profile/edit_address/',views.addressbook, name = 'edit_address'),
    path('home/profile/edit_baddress/',views.editBillingAdress, name = 'edit_address'),



]
