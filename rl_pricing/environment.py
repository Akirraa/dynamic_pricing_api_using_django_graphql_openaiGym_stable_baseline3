import gymnasium as gym
from gymnasium import spaces
import numpy as np
from products.models import Product, ProductPriceHistory
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

class ProductPricingEnv(gym.Env):
    """Custom Environment for product pricing following Gymnasium interface"""

    def __init__(self, product_id):
        super(ProductPricingEnv, self).__init__()
        self.product_id = product_id
        self.product = Product.objects.get(id=product_id)

        # Define 5 discrete actions
        # 0: -10%, 1: -5%, 2: no change, 3: +5%, 4: +10%
        self.action_space = spaces.Discrete(5)

        INF = np.finfo(np.float32).max
        self.observation_space = spaces.Box(
            low=np.array([
                self.product.min_price,
                self.product.min_price,
                0,
                0,
                0
            ], dtype=np.float32),
            high=np.array([
                self.product.max_price,
                self.product.max_price,
                INF,
                30,
                INF
            ], dtype=np.float32),
            dtype=np.float32
        )

        self.current_step = 0
        self.max_steps = 100
        self.state = None

    def _get_state(self):
        """Helper to get the current state"""
        week_ago = timezone.now() - timedelta(days=7)
        sales_data = ProductPriceHistory.objects.filter(
            product=self.product,
            timestamp__gte=week_ago
        ).order_by('timestamp')

        if sales_data.exists():
            sales_count = sales_data.count()
            avg_sales = sales_count / 7
        else:
            avg_sales = 0.0

        last_sale = sales_data.last()
        days_since_last = (timezone.now() - last_sale.timestamp).days if last_sale else 30

        return np.array([
            float(self.product.current_price),
            float(self.product.base_price),
            float(self.product.stock_quantity),
            float(days_since_last),
            float(avg_sales)
        ], dtype=np.float32)

    def reset(self, *, seed=None, options=None):
        """Reset environment state"""
        super().reset(seed=seed)
        self.product.refresh_from_db()
        self.current_step = 0
        self.state = self._get_state()
        return self.state, {}

    def step(self, action):
        """Apply an action (discrete price adjustment)"""
        self.current_step += 1

        price_change_percentages = [-0.10, -0.05, 0.0, 0.05, 0.10]
        price_change = price_change_percentages[action]

        current_price = float(self.product.current_price)
        new_price = current_price * (1 + price_change)

        # Clip price within allowed range
        new_price = np.clip(new_price, self.product.min_price, self.product.max_price)

        # Save the new price to Product
        self.product.current_price = new_price
        self.product.save()

        # Record a new entry in ProductPriceHistory
        ProductPriceHistory.objects.create(
            product=self.product,
            price=new_price,
            change_percentage=price_change * 100,  # Save as percentage
            timestamp=timezone.now()
        )

        # Update state
        self.state = self._get_state()

        # Calculate reward
        reward = self._calculate_reward(new_price)

        done = self.current_step >= self.max_steps
        truncated = False

        return self.state, reward, done, truncated, {}

    

    def _calculate_reward(self, new_price):
        # Ensure new_price is a Decimal
        if not isinstance(new_price, Decimal):
            new_price = Decimal(str(new_price))

        cost_price = self.product.cost_price  # Already a Decimal from model
        profit_margin = (new_price - cost_price) / new_price
        return float(profit_margin)  # Convert to float if necessary for the RL model


    def render(self, mode="human"):
        print(f"Step: {self.current_step}, Price: {self.product.current_price:.2f}")

    def close(self):
        pass
