from django.contrib import admin
from .models import App, UserPurchase

@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')

@admin.register(UserPurchase)
class UserPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'app', 'status', 'purchase_date')
    list_filter = ('status',)
    search_fields = ('user__username', 'app__name')