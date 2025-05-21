def cart_item_count(request):
    cart = request.session.get('cart', {})
    count = sum(item['quantity'] for item in cart.values())
    return {'all_cart': count}
