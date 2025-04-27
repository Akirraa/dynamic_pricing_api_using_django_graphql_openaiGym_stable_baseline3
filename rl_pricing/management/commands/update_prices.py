from django.core.management.base import BaseCommand
from products.models import Product
from rl_pricing.trainer import PricingModelTrainer

class Command(BaseCommand):
    help = 'Updates product prices using RL models'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--train-new',
            action='store_true',
            help='Train new models instead of using existing ones'
        )
        parser.add_argument(
            '--timesteps',
            type=int,
            default=5000,
            help='Number of timesteps to train if training new models'
        )
    
    def handle(self, *args, **options):
        self.stdout.write("Starting price update process...")
        
        products = Product.objects.all()
        
        for product in products:
            self.stdout.write(f"\nProcessing product: {product.name} (ID: {product.id})")
            
            trainer = PricingModelTrainer(product.id)
            
            try:
                if options['train_new']:
                    self.stdout.write(f"Training new model for {product.name}...")
                    trainer.train(total_timesteps=options['timesteps'])
                else:
                    self.stdout.write(f"Loading or creating model for {product.name}...")
                    trainer.load_or_create_model()
                
                    current_price = float(product.current_price)

                    if product.pricing_strategy == 'RL':
                        price_change = trainer.predict_price_change()
                        new_price = current_price * (1 + price_change)
                        strategy_used = "RL Model"
                    else:  # STATIC pricing
                        price_change = 0.02  # +2% increase manually
                        new_price = current_price * (1 + price_change)
                        strategy_used = "Static Pricing (+2%)"

                    # Clamp the price between min and max
                    new_price = max(float(product.min_price), min(float(product.max_price), new_price))

                
                if abs(new_price - current_price) > 0.01:  # Only update if change > 1 cent
                    product.current_price = new_price
                    product.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Price updated from ${current_price:.2f} to ${new_price:.2f} "
                            f"(change: {price_change*100:.1f}%)"
                        )
                    )
                else:
                    self.stdout.write(
                        f"No significant price change needed (would be ${new_price:.2f})"
                    )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error processing {product.name}: {str(e)}")
                )
                # Print full traceback for debugging
                import traceback
                self.stdout.write(self.style.ERROR(traceback.format_exc()))
        
        self.stdout.write(self.style.SUCCESS("\nPrice update process completed!"))