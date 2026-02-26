from .models import Cart

def cart_count(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        count = sum(item.quantity for item in cart.items.all())
    else:
        count = 0

    return {
        "cart_count": count
    }