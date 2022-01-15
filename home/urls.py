from django.urls import path

from . import views
urlpatterns = [
    path('', views.index),
    path('login', views.login),
    path('logout', views.logout),
    path('registration', views.registration),
    path('lichtrinh', views.lichtrinh),
    path('bus_route/search', views.search),
    path('bus_stop', views.benxe),
    path('bus_stop/dd=<str:dd>/<str:mtr>', views.bx_diemxp),
    path('customer/0', views.login),
    path('kh/ttcn', views.ttcn),
    path('kh/vedadat', views.vedadat),
    path('customer/thanhtoan', views.thanhtoan1),
    path('customer/update_cart', views.update_cart),
    path('customer/thanhtoan/tt', views.payment),
    path('customer/cart', views.giohang),
    path('customer/get_tb', views.get_tb),
    path('bus_route', views.lichtrinhKH),
    # path('customer/bus_route', views.lichtrinhKH),
    path('check', views.check),
    path('bus_stop/dd=<str:dd>&xp=<str:xp>', views.cttd),
    path('bus_stop/dd=<str:dd>&xp=<str:xp>/lt/<str:mt>', views.ltr),
    path('customer/add_item/<str:mlt>', views.add_item, name='h'),
    path('customer/delete_item/<str:mlt>', views.delete_item, name='get_table'),
    path('customer/ticket', views.ticket),
    path('customer/ticket_cancel', views.ticket_cancel),
    path('Home/index', views.dangky),
    path('checkTK', views.checkTK),

]