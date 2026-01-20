from django.contrib import admin
from .models import Payment, Order, OrderProduct

# This allows you to see the products purchased inside the order detail page
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    # What columns show up in the list view
    list_display = ['order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'status', 'is_ordered', 'created_at']
    
    # Filter sidebar on the right
    list_filter = ['status', 'is_ordered']
    
    # Search box at the top
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    
    list_per_page = 20
    
    # This puts the purchased products table inside the Order page
    inlines = [OrderProductInline]

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)