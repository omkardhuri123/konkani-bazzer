from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product', 'quantity', 'price', 'get_total']
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['thumbnail', 'name', 'price', 'stock', 'featured', 'category', 'is_active']
    list_editable = ['price', 'stock', 'featured', 'is_active']
    list_filter = ['category', 'featured', 'is_active']
    search_fields = ['name', 'slug', 'category__name']
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='Image')
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;" />', obj.image.url)
        return '-'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ['id', 'user', 'total', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['user__username', 'id', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


# Site branding
admin.site.site_header = "Kokanibazaar Admin"
admin.site.site_title = "Kokanibazaar Dashboard"
admin.site.index_title = "Administration"
