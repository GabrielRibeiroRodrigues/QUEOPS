from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from store.models import Product
from .cart import Cart
import json


class CartDetailView(View):
    """View para exibir o carrinho"""
    
    def get(self, request):
        cart = Cart(request)
        return render(request, 'cart/cart_detail.html', {
            'cart': cart
        })


@require_POST
def cart_add(request, product_id):
    """Adiciona produto ao carrinho"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1
    
    # Verificar se há estoque suficiente
    if product.track_stock and product.stock_quantity < quantity:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Estoque insuficiente'
            })
        messages.error(request, 'Estoque insuficiente para este produto.')
        return redirect('store:product_detail', slug=product.slug)
    
    cart.add(product, quantity=quantity)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Produto adicionado ao carrinho',
            'cart_total_items': len(cart),
            'cart_total_price': float(cart.get_total_price())
        })
    
    messages.success(request, f'{product.name} foi adicionado ao carrinho.')
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """Remove produto do carrinho"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Produto removido do carrinho',
            'cart_total_items': len(cart),
            'cart_total_price': float(cart.get_total_price())
        })
    
    messages.success(request, f'{product.name} foi removido do carrinho.')
    return redirect('cart:cart_detail')


@require_POST
def cart_update(request, product_id):
    """Atualiza a quantidade de um produto no carrinho"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            # Se quantidade for 0 ou negativa, remove o produto
            cart.remove(product)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Produto removido do carrinho',
                    'cart_total_items': len(cart),
                    'cart_total_price': float(cart.get_total_price())
                })
            messages.success(request, f'{product.name} foi removido do carrinho.')
            return redirect('cart:cart_detail')
    except (ValueError, TypeError):
        quantity = 1
    
    # Verificar estoque
    if product.track_stock and product.stock_quantity < quantity:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Estoque insuficiente'
            })
        messages.error(request, 'Estoque insuficiente para este produto.')
        return redirect('cart:cart_detail')
    
    cart.add(product, quantity=quantity, override_quantity=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Carrinho atualizado',
            'cart_total_items': len(cart),
            'cart_total_price': float(cart.get_total_price())
        })
    
    messages.success(request, 'Carrinho atualizado com sucesso.')
    return redirect('cart:cart_detail')


def cart_clear(request):
    """Limpa todo o carrinho"""
    cart = Cart(request)
    cart.clear()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Carrinho limpo'
        })
    
    messages.success(request, 'Carrinho foi limpo.')
    return redirect('cart:cart_detail')


def cart_summary(request):
    """Retorna resumo do carrinho em JSON para AJAX"""
    cart = Cart(request)
    return JsonResponse({
        'total_items': len(cart),
        'total_price': float(cart.get_total_price()),
        'items': [
            {
                'product_id': item['product'].id,
                'product_name': item['product'].name,
                'quantity': item['quantity'],
                'price': float(item['price']),
                'total_price': float(item['total_price'])
            }
            for item in cart
        ]
    })