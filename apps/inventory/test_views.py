from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from apps.product.models import Product
from django.db import models
import json

@csrf_exempt
@require_http_methods(["POST"])
def simulate_stock_update(request):
    """Test endpoint to simulate stock updates and trigger alerts"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        new_stock = data.get('new_stock')
        
        if not product_id or new_stock is None:
            return JsonResponse({
                'error': 'product_id and new_stock are required'
            }, status=400)
        
        # Get product and update stock
        product = Product.objects.get(id=product_id)
        old_stock = product.current_stock
        product.current_stock = new_stock
        product.save()  # This triggers the signal
        
        return JsonResponse({
            'success': True,
            'message': f'Stock updated for {product.name}',
            'product': {
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'old_stock': old_stock,
                'new_stock': product.current_stock,
                'threshold': product.low_stock_threshold,
                'alert_triggered': product.current_stock <= product.low_stock_threshold
            }
        })
        
    except Product.DoesNotExist:
        return JsonResponse({
            'error': 'Product not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_low_stock_products(request):
    """Get all products with low stock"""
    low_stock_products = Product.objects.filter(
        current_stock__lte=models.F('low_stock_threshold')
    ).select_related('category')
    
    products_data = []
    for product in low_stock_products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'current_stock': product.current_stock,
            'threshold': product.low_stock_threshold,
            'category': product.category.name if product.category else None
        })
    
    return JsonResponse({
        'low_stock_products': products_data,
        'count': len(products_data)
    })