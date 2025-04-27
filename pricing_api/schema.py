import graphene
from products.schema import ProductType, ProductCategoryType, Query as ProductsQuery
from graphene_django.debug import DjangoDebug

class Query(ProductsQuery, graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name='__debug')

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
            
            return UpdatePrice(
                product=product,
                success=True,
                message=f"{message} to ${new_price:.2f}",
                price_change_percent=price_change*100
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

class Mutation(graphene.ObjectType):
    update_price = UpdatePrice.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)