from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('applist/', views.applist, name='applist'),
    path('applist/<str:app_name>/', views.app_detail, name='app_detail'),
    path('search/', views.search_app, name='search_app'),
    path('install_app/<str:app_name>/', views.install_app_route, name='install_app_route'),
    path('apps/category/<str:category>/', views.applist, name='applist_by_category'),
    #=============================Admin==========================================

    path('admin/', views.admin_page, name='admin_page'),
    path('admin/search/', views.admin_search_app, name='admin_search_app'),
    path('admin/category/<str:category>/', views.admin_page, name='admin_by_category'),
    path('admin/add/', views.add_app, name='add_app'),
    path('admin/edit/<int:id>/', views.edit_app, name='edit_app'),
    path('admin/delete/<int:id>/', views.delete_app, name='delete_app'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    #=============================Registration================================

    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),  # Profile edit view
    path('password_change/', views.change_password, name='password_change'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]
