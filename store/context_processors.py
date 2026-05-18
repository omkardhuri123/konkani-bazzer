from decimal import Decimal

from .models import Product


def cart(request):
    cart = request.session.get("cart", {}) or {}
    total_items = sum(cart.values())
    cart_total = Decimal("0.00")
    cart_items = []

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(pk=int(product_id), is_active=True)
        except (Product.DoesNotExist, ValueError):
            continue

        subtotal = product.price * quantity
        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )
        cart_total += subtotal

    return {
        "cart_total_items": total_items,
        "cart_items": cart_items,
        "cart_total": cart_total,
    }
