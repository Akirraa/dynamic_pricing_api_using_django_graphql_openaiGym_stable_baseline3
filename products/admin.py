from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Product, ProductCategory, ProductPriceHistory
from rl_pricing.tasks import update_product_prices  # For admin action

# Inline to display price history inside the Product detail page
class ProductPriceHistoryInline(admin.TabularInline):
    model = ProductPriceHistory
    extra = 0
    readonly_fields = ['price', 'timestamp', 'change_percentage', 'units_sold', 'revenue']
    ordering = ['-timestamp']  # Newest first
    verbose_name_plural = 'Price History Records'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'current_price', 
        'pricing_strategy',  # ✅ Keep only pricing_strategy
        'stock_quantity', 
        'last_price_update'
    )
    list_filter = (
        'pricing_strategy',   # ✅ Keep this
        'category'
    )
    search_fields = ('name',)
    inlines = [ProductPriceHistoryInline]
    readonly_fields = ['price_history_chart']
    actions = ['trigger_update_prices']  # ⭐ Admin Action!

    def price_history_chart(self, obj):
        """ Display a mini price history chart (can be upgraded later). """
        dummy_url = (
            f"https://quickchart.io/chart"
            f"?c={{type:'line',data:{{labels:['Jan','Feb','Mar'],datasets:[{{label:'Price',data:[100,120,110]}}]}}}}"
        )
        return mark_safe(f'<img src="{dummy_url}" width="400">')
    price_history_chart.short_description = "Price History Chart"

    def trigger_update_prices(self, request, queryset):
        """ Admin action: trigger Celery price update. """
        update_product_prices.delay()
        self.message_user(request, "Price updates started in background via Celery!")
    trigger_update_prices.short_description = "Update Prices (Celery Task)"

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(ProductPriceHistory)
class ProductPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'timestamp', 'change_percentage', 'units_sold', 'revenue')
    list_filter = ('timestamp',)  
    search_fields = ('product__name',)
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
