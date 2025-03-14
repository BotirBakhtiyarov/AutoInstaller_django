from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('applist/', views.applist, name='applist'),
    path('applist/<str:app_name>/', views.app_detail, name='app_detail'),
    path('search/', views.search_app, name='search_app'),
    path('install_app/<str:app_name>/', views.install_app_route, name='install_app_route'),
    path('apps/category/<str:category>/', views.applist, name='applist_by_category'),
    #=============================Admin==========================================
    path('payment/<int:app_id>/', views.payment_view, name='payment'),
    path('payment/notify/', views.payment_notify, name='payment_notify'),
    path('payment/status/<str:transaction_id>/', views.check_payment_status, name='check_payment_status'),
    path('api/install/<str:app_name>/', views.api_install_app, name='api_install_app'),
]

