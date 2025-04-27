from celery import shared_task
from django.utils import timezone
from rl_pricing.trainer import PricingModelTrainer
from products.models import Product

@shared_task
def retrain_rl_models(timesteps=1000):
    """
    Retrain RL models for all products using the given timesteps.
    """
    products = Product.objects.filter(pricing_strategy='RL')  # Only retrain RL products
    for product in products:
        try:
            trainer = PricingModelTrainer(product.id)
            trainer.train(total_timesteps=timesteps)
            print(f"✅ Trained RL model for product {product.name}")
        except Exception as e:
            print(f"❌ Failed to train model for {product.name}: {e}")

@shared_task
def update_product_prices():
    """
    Update prices for products based on their RL-trained models.
    """
    products = Product.objects.filter(pricing_strategy='RL')  # Only update RL products

    for product in products:
        try:
            trainer = PricingModelTrainer(product.id)
            model = trainer.load_or_create_model()  # Safe: will train if model doesn't exist

            # Simulate environment state
            env_state = [
                float(product.current_price),
                float(product.stock_quantity),
            ]

            # Predict action
            action, _ = model.predict(env_state, deterministic=True)

            # Interpret action to price change percentage
            change_percentage = (action - 2) * 2.5  # Example: if 0 -> -5%, 2 -> 0%, 4 -> +5%

            # Calculate new price
            new_price = float(product.current_price) * (1 + change_percentage / 100)
            new_price = max(float(product.min_price), min(new_price, float(product.max_price)))

            # Update product
            product.current_price = new_price
            product.last_price_update = timezone.now()
            product.save()

            # Create a history record
            product.price_history.create(
                price=new_price,
                change_percentage=change_percentage,
            )

            print(f"✅ Updated price for {product.name}: {product.current_price:.2f}")

        except Exception as e:
            print(f"❌ Failed to update price for {product.name}: {e}")

    return "✅ All RL product prices updated."
