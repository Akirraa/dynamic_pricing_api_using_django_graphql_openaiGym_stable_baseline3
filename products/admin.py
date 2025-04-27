from django.contrib import admin
from .models import Product, ProductCategory, ProductPriceHistory



admin.site.register(ProductCategory)
admin.site.register(ProductPriceHistory)
admin.site.register(Product)