import graphene
from products.models import Product, ProductCategory
from products.schema import ProductType, ProductCategoryType

class CreateProductCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=False)

    product_category = graphene.Field(ProductCategoryType)

    @classmethod
    def mutate(cls, root, info, name, description=""):
        category = ProductCategory(name=name, description=description)
        category.save()
        return CreateProductCategory(product_category=category)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=False)
        category_id = graphene.Int(required=True)
        base_price = graphene.Decimal(required=True)
        current_price = graphene.Decimal(required=True)
        cost_price = graphene.Decimal(required=True)
        stock_quantity = graphene.Int(required=True)
        min_price = graphene.Decimal(required=True)
        max_price = graphene.Decimal(required=True)
        pricing_strategy = graphene.String(required=False, default_value="RL")

    product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, root, info, name, description, category_id,
               base_price, current_price, cost_price,
               stock_quantity, min_price, max_price, pricing_strategy):
        category = ProductCategory.objects.get(pk=category_id)
        product = Product(
            name=name,
            description=description,
            category=category,
            base_price=base_price,
            current_price=current_price,
            cost_price=cost_price,
            stock_quantity=stock_quantity,
            min_price=min_price,
            max_price=max_price,
            pricing_strategy=pricing_strategy
        )
        product.save()
        return CreateProduct(product=product)
