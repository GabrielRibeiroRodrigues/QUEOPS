from django.conf import settings
from .cart import Cart


def cart(request):
    """
    Context processor que disponibiliza o carrinho em todos os templates.
    """
    return {'cart': Cart(request)}
