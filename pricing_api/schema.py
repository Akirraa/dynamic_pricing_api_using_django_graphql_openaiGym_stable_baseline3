import graphene
from products.schema import ProductType, ProductCategoryType, Query as ProductsQuery
from graphene_django.debug import DjangoDebug
from rl_pricing.tasks import update_product_prices  # make sure this exists

class Query(ProductsQuery, graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='_debug')  # ✅ renamed correctly

# ---------------- Update Price for a single product ----------------
class UpdatePrice(graphene.Mutation):
    class Arguments:
        product_id = graphene.Int(required=True)
        train_new = graphene.Boolean(default_value=False)
        timesteps = graphene.Int(default_value=5000)
    
    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()
    price_change_percent = graphene.Float()
    
    def mutate(self, info, product_id, train_new, timesteps):
        from rl_pricing.trainer import PricingModelTrainer
        from products.models import Product
        
        try:
            product = Product.objects.get(id=product_id)
            trainer = PricingModelTrainer(product_id)
            
            if train_new:
                model = trainer.train(total_timesteps=timesteps)
                message = "New model trained and price updated"
            else:
                model = trainer.load_or_create_model()
                message = "Price updated using existing model"
            
            current_price = float(product.current_price)
            price_change = trainer.predict_price_change()
            new_price = current_price * (1 + price_change)
            new_price = max(float(product.min_price), min(float(product.max_price), new_price))
            
            product.current_price = new_price
            product.save()
            product.refresh_from_db() 
            
            return UpdatePrice(
                product=product,
                success=True,
                message=f"{message} to ${new_price:.2f}",
                price_change_percent=price_change * 100
            )
            
        except Product.DoesNotExist:
            return UpdatePrice(
                product=None,
                success=False,
                message=f"Product with ID {product_id} not found",
                price_change_percent=0
            )
        except Exception as e:
            return UpdatePrice(
                product=None,
                success=False,
                message=f"Error updating price: {str(e)}",
                price_change_percent=0
            )

# ---------------- Update All Product Prices using Celery ----------------
class UpdateAllPrices(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info):
        try:
            update_product_prices.delay()
            return UpdateAllPrices(success=True, message="Price update started in background.")
        except Exception as e:
            return UpdateAllPrices(success=False, message=f"Failed to start price update: {str(e)}")

# ---------------- Create a Product ----------------
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        category_id = graphene.Int(required=True)
        base_price = graphene.Decimal(required=True)
        current_price = graphene.Decimal(required=True)
        cost_price = graphene.Decimal(required=True)
        stock_quantity = graphene.Int(required=True)
        min_price = graphene.Decimal(required=True)
        max_price = graphene.Decimal(required=True)
        pricing_strategy = graphene.String(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, **kwargs):
        from products.models import Product, ProductCategory

        try:
            category = ProductCategory.objects.get(id=kwargs['category_id'])

            product = Product.objects.create(
                name=kwargs['name'],
                description=kwargs.get('description', ''),
                category=category,
                base_price=kwargs['base_price'],
                current_price=kwargs['current_price'],
                cost_price=kwargs['cost_price'],
                stock_quantity=kwargs['stock_quantity'],
                min_price=kwargs['min_price'],
                max_price=kwargs['max_price'],
                pricing_strategy=kwargs['pricing_strategy'],
            )
            return CreateProduct(product=product)

        except ProductCategory.DoesNotExist:
            raise Exception("Category does not exist")

# ---------------- Main Schema ----------------
class Mutation(graphene.ObjectType):
    update_price = UpdatePrice.Field()
    update_all_prices = UpdateAllPrices.Field()
    create_product = CreateProduct.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
