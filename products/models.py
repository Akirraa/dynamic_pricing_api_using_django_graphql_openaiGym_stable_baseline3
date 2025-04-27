from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    current_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock_quantity = models.PositiveIntegerField(default=0)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    max_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    last_price_update = models.DateTimeField(auto_now=True)

    USE_RL_CHOICES = [
        ('RL', 'Reinforcement Learning Pricing'),
        ('STATIC', 'Traditional Static Pricing')
    ]
    pricing_strategy = models.CharField(
        max_length=10,
        choices=USE_RL_CHOICES,
        default='RL',
        help_text="RL = Reinforcement Learning Pricing, STATIC = Traditional Static Pricing"
    )
    last_strategy_change = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class ProductPriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    change_percentage = models.FloatField(default=0.0) 
    
    units_sold = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.product.name} - {self.price} at {self.timestamp}"
