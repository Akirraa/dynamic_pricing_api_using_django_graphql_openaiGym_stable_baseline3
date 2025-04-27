import graphene
from graphene_django import DjangoObjectType
from .models import Product, ProductCategory, ProductPriceHistory

class ProductCategoryType(DjangoObjectType):
    class Meta:
        model = ProductCategory
        fields = "__all__"

class ProductPriceHistoryType(DjangoObjectType):
    class Meta:
        model = ProductPriceHistory
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"
    
    price_history = graphene.List(ProductPriceHistoryType)
    
    def resolve_price_history(self, info):
        return self.price_history.all().order_by('-timestamp')[:10]  # Last 10 price changes
    
    


class Query(graphene.ObjectType):
    all_products = graphene.List(ProductType)
    product = graphene.Field(ProductType, id=graphene.Int(required=True))
    products_by_category = graphene.List(ProductType, category_id=graphene.Int(required=True))
    
    def resolve_all_products(self, info):
        return Product.objects.all()
    
    def resolve_product(self, info, id):
        return Product.objects.get(id=id)
    
    def resolve_products_by_category(self, info, category_id):
        return Product.objects.filter(category_id=category_id)