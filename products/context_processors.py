from products.models import Product

def pricing_admin_context(request):
    if not request.path.startswith('/admin/'):
        return {}
    
    dynamic_products = Product.objects.all()  # Filter for dynamic pricing products in real app
    recently_updated = dynamic_products.order_by('-last_price_update')[:5]
    
    # Calculate average price adjustment
    adjustments = []
    for p in dynamic_products:
        if p.base_price > 0:
            diff = (p.current_price - p.base_price) / p.base_price * 100
            adjustments.append(diff)
    
    avg_adjustment = sum(adjustments) / len(adjustments) if adjustments else 0
    
    # Add price diff percent to recently updated
    for p in recently_updated:
        p.price_diff_percent = ((p.current_price - p.base_price) / p.base_price * 100) if p.base_price > 0 else 0
    
    return {
        'dynamic_pricing_count': dynamic_products.count(),
        'avg_price_adjustment': avg_adjustment,
        'recently_updated': recently_updated,
    }