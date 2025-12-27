from django.db import transaction
from datetime import datetime, timedelta
from django.db.models import Avg, Sum
from .models import Purchase, PurchaseItem, ProductSupplier, PurchaseOrderSuggestion
from apps.inventory.services import InventoryService
from apps.sales.models import SaleItem

class PurchaseService:
    @staticmethod
    @transaction.atomic
    def create_purchase(supplier_id: int, items: list):
        purchase = Purchase.objects.create(supplier_id=supplier_id)

        total = 0
        for item in items:
            total += item["qty"] * item["unit_cost"]
            PurchaseItem.objects.create(
                purchase=purchase,
                product_id=item["product_id"],
                qty=item["qty"],
                unit_cost=item["unit_cost"]
            )
            InventoryService.increase_stock(item["product_id"], item["qty"])

        purchase.total_amount = total
        purchase.save()
        return purchase


class PurchaseOrderSuggestionService:
    @staticmethod
    def generate_suggestion_for_product(product_id: int, current_stock: int, threshold: int):
        """Generate purchase order suggestion when stock is low"""
        try:
            from apps.product.models import Product
            product = Product.objects.get(id=product_id)
            
            # Find preferred supplier
            supplier_info = ProductSupplier.objects.filter(
                product_id=product_id, 
                is_preferred=True
            ).first()
            
            if not supplier_info:
                # Fallback to any supplier for this product
                supplier_info = ProductSupplier.objects.filter(product_id=product_id).first()
            
            if not supplier_info:
                return None
            
            # Calculate suggested quantity based on sales history
            suggested_qty = PurchaseOrderSuggestionService._calculate_order_quantity(
                product_id, current_stock, threshold, supplier_info.minimum_order_qty
            )
            
            total_cost = suggested_qty * supplier_info.unit_cost
            
            # Create suggestion
            suggestion = PurchaseOrderSuggestion.objects.create(
                product=product,
                supplier=supplier_info.supplier,
                suggested_qty=suggested_qty,
                unit_cost=supplier_info.unit_cost,
                total_cost=total_cost,
                reason=f"Stock alert: {current_stock} units remaining (threshold: {threshold}). "
                       f"Suggested based on {supplier_info.lead_time_days}-day lead time and sales history."
            )
            
            return suggestion
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to generate PO suggestion for product {product_id}: {e}")
            return None
    
    @staticmethod
    def _calculate_order_quantity(product_id: int, current_stock: int, threshold: int, min_order_qty: int):
        """Calculate optimal order quantity based on sales history"""
        # Get average daily sales for last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        avg_daily_sales = SaleItem.objects.filter(
            product_id=product_id,
            sale__created_at__gte=thirty_days_ago,
            sale__status='COMPLETED'
        ).aggregate(
            total_sold=Sum('qty')
        )['total_sold'] or 0
        
        daily_avg = avg_daily_sales / 30 if avg_daily_sales > 0 else 1
        
        # Calculate for 30 days of stock + safety buffer
        safety_days = 7  # 1 week safety stock
        target_stock = int(daily_avg * (30 + safety_days))
        
        # Order quantity = target stock - current stock
        order_qty = max(target_stock - current_stock, min_order_qty)
        
        return order_qty
    
    @staticmethod
    @transaction.atomic
    def approve_suggestion(suggestion_id: int, user_id: int = None):
        """Approve a purchase order suggestion and convert to actual purchase"""
        suggestion = PurchaseOrderSuggestion.objects.get(id=suggestion_id)
        
        if suggestion.status != 'PENDING':
            raise ValueError("Only pending suggestions can be approved")
        
        # Create actual purchase order
        purchase = Purchase.objects.create(
            supplier=suggestion.supplier,
            created_by_id=user_id,
            total_amount=suggestion.total_cost
        )
        
        PurchaseItem.objects.create(
            purchase=purchase,
            product=suggestion.product,
            qty=suggestion.suggested_qty,
            unit_cost=suggestion.unit_cost,
            line_total=suggestion.total_cost
        )
        
        # Update suggestion status
        suggestion.status = 'CONVERTED'
        suggestion.reviewed_at = datetime.now()
        suggestion.reviewed_by_id = user_id
        suggestion.save()
        
        return purchase
