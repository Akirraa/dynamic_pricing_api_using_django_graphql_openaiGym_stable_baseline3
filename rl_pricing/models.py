from django.db import models
from products.models import Product

class RLModel(models.Model):
    ALGORITHM_CHOICES = [
        ('DQN', 'Deep Q-Network'),
        ('PPO', 'Proximal Policy Optimization'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    algorithm = models.CharField(max_length=10, choices=ALGORITHM_CHOICES)
    model_file = models.FileField(upload_to='rl_models/')
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('product', 'algorithm')
        ordering = ['product__name', 'algorithm']
    
    def __str__(self):
        return f"{self.product.name} - {self.get_algorithm_display()} (v{self.version})"

class TrainingSession(models.Model):
    model = models.ForeignKey(RLModel, on_delete=models.CASCADE, related_name='training_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    successful = models.BooleanField(default=False)
    log_output = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Training {self.model} at {self.started_at}"