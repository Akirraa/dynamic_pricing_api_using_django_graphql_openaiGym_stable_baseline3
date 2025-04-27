import random
from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    help = 'Randomly assign products to pricing strategies (STATIC or RL) for A/B testing.'

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            product.pricing_strategy = random.choice(['STATIC', 'RL'])
            product.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully assigned pricing strategies to {products.count()} products.'))
