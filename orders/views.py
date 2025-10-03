from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import json
import mercadopago
import logging

from .models import Order, OrderItem, Payment, ShippingRate
from cart.cart import Cart
from store.models import Product
from accounts.models import Address

logger = logging.getLogger(__name__)


class OrderListView(LoginRequiredMixin, ListView):
    """View para listar pedidos do usuário"""
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    """View para detalhes do pedido"""
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@login_required
def checkout(request):
    """View para processo de checkout"""
    cart = Cart(request)
    
    if not cart:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Criar pedido
                order = create_order_from_cart(request, cart)
                
                # Limpar carrinho
                cart.clear()
                
                messages.success(request, f'Pedido {order.order_number} criado com sucesso!')
                return redirect('orders:payment', order_id=order.id)
                
        except Exception as e:
            logger.error(f"Erro ao criar pedido: {str(e)}")
            messages.error(request, 'Erro ao processar pedido. Tente novamente.')
    
    # Obter endereços do usuário
    user_addresses = []
    if hasattr(request.user, 'addresses'):
        user_addresses = request.user.addresses.filter(is_active=True)
    
    # Calcular opções de frete
    shipping_options = calculate_shipping_options(cart)
    
    context = {
        'cart': cart,
        'user_addresses': user_addresses,
        'shipping_options': shipping_options,
    }
    
    return render(request, 'orders/checkout.html', context)


def create_order_from_cart(request, cart):
    """Cria um pedido a partir do carrinho"""
    user = request.user if request.user.is_authenticated else None
    
    # Dados do formulário de checkout
    shipping_data = {
        'first_name': request.POST.get('first_name'),
        'last_name': request.POST.get('last_name'),
        'email': request.POST.get('email'),
        'phone': request.POST.get('phone'),
        'shipping_address_line_1': request.POST.get('address_line_1'),
        'shipping_address_line_2': request.POST.get('address_line_2', ''),
        'shipping_city': request.POST.get('city'),
        'shipping_state': request.POST.get('state'),
        'shipping_postal_code': request.POST.get('postal_code'),
        'shipping_country': request.POST.get('country', 'Brasil'),
    }
    
    # Calcular valores
    subtotal = cart.get_total_price()
    shipping_cost = Decimal(request.POST.get('shipping_cost', '0.00'))
    total = subtotal + shipping_cost
    
    # Criar pedido
    order = Order.objects.create(
        user=user,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        total=total,
        shipping_method=request.POST.get('shipping_method', ''),
        **shipping_data
    )
    
    # Criar itens do pedido
    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            product_name=item['product'].name,
            product_sku=item['product'].sku,
            quantity=item['quantity'],
            unit_price=item['price'],
            total_price=item['total_price']
        )
        
        # Reduzir estoque
        item['product'].reduce_stock(item['quantity'])
    
    return order


def calculate_shipping_options(cart):
    """Calcula opções de frete para o carrinho"""
    total_weight = sum(
        Decimal(str(item['product'].weight or 0)) * item['quantity'] 
        for item in cart
    )
    
    shipping_rates = ShippingRate.objects.filter(
        is_active=True,
        min_weight__lte=total_weight,
        max_weight__gte=total_weight
    )
    
    options = []
    for rate in shipping_rates:
        cost = rate.calculate_shipping_cost(total_weight)
        options.append({
            'id': rate.id,
            'name': rate.name,
            'carrier': rate.carrier,
            'cost': cost,
            'delivery_time': rate.delivery_time,
            'description': f"{rate.carrier} - {rate.name} (até {rate.delivery_time} dias úteis)"
        })
    
    return options


@login_required
def payment(request, order_id):
    """View para pagamento do pedido"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'completed':
        messages.info(request, 'Este pedido já foi pago.')
        return redirect('orders:order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'mercadopago_public_key': settings.MERCADOPAGO_PUBLIC_KEY,
    }
    
    return render(request, 'orders/payment.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def create_payment(request, order_id):
    """Cria preferência de pagamento no Mercado Pago"""
    try:
        order = get_object_or_404(Order, id=order_id)
        
        # Configurar SDK do Mercado Pago
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        
        # Criar itens para o Mercado Pago
        items = []
        for item in order.items.all():
            items.append({
                "title": item.product_name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "currency_id": "BRL"
            })
        
        # Adicionar frete como item
        if order.shipping_cost > 0:
            items.append({
                "title": f"Frete - {order.shipping_method}",
                "quantity": 1,
                "unit_price": float(order.shipping_cost),
                "currency_id": "BRL"
            })
        
        # Configurar preferência
        preference_data = {
            "items": items,
            "payer": {
                "name": order.first_name,
                "surname": order.last_name,
                "email": order.email,
                "phone": {
                    "number": order.phone
                } if order.phone else None
            },
            "back_urls": {
                "success": request.build_absolute_uri(f"/orders/{order.id}/payment-success/"),
                "failure": request.build_absolute_uri(f"/orders/{order.id}/payment-failure/"),
                "pending": request.build_absolute_uri(f"/orders/{order.id}/payment-pending/")
            },
            "auto_return": "approved",
            "external_reference": order.order_number,
            "statement_descriptor": "LOJA ONLINE"
        }
        
        # Criar preferência
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        
        # Salvar pagamento
        payment = Payment.objects.create(
            order=order,
            payment_method='mercadopago',
            amount=order.total,
            gateway='mercadopago',
            gateway_transaction_id=preference['id']
        )
        
        return JsonResponse({
            'status': 'success',
            'preference_id': preference['id'],
            'init_point': preference['init_point']
        })
        
    except Exception as e:
        logger.error(f"Erro ao criar pagamento: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Erro ao processar pagamento. Tente novamente.'
        }, status=500)


@login_required
def payment_success(request, order_id):
    """View para pagamento aprovado"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Atualizar status do pedido
    order.status = 'confirmed'
    order.payment_status = 'completed'
    order.save()
    
    # Enviar email de confirmação
    send_order_confirmation_email(order)
    
    messages.success(request, 'Pagamento aprovado! Seu pedido foi confirmado.')
    return render(request, 'orders/payment_success.html', {'order': order})


@login_required
def payment_failure(request, order_id):
    """View para pagamento rejeitado"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    messages.error(request, 'Pagamento não foi aprovado. Tente novamente.')
    return render(request, 'orders/payment_failure.html', {'order': order})


@login_required
def payment_pending(request, order_id):
    """View para pagamento pendente"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    order.payment_status = 'processing'
    order.save()
    
    messages.info(request, 'Pagamento em processamento. Você será notificado quando for aprovado.')
    return render(request, 'orders/payment_pending.html', {'order': order})


@csrf_exempt
@require_http_methods(["POST"])
def mercadopago_webhook(request):
    """Webhook para receber notificações do Mercado Pago"""
    try:
        data = json.loads(request.body)
        
        if data.get('type') == 'payment':
            payment_id = data['data']['id']
            
            # Consultar pagamento no Mercado Pago
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)
            
            if payment_info['status'] == 200:
                payment_data = payment_info['response']
                external_reference = payment_data.get('external_reference')
                
                try:
                    order = Order.objects.get(order_number=external_reference)
                    payment = order.payments.filter(
                        gateway_transaction_id=payment_data.get('preference_id')
                    ).first()
                    
                    if payment:
                        # Atualizar status do pagamento
                        payment.status = map_mercadopago_status(payment_data['status'])
                        payment.gateway_response = payment_data
                        payment.save()
                        
                        # Atualizar pedido
                        if payment.status == 'completed':
                            order.status = 'confirmed'
                            order.payment_status = 'completed'
                            send_order_confirmation_email(order)
                        elif payment.status == 'failed':
                            order.payment_status = 'failed'
                        
                        order.save()
                        
                except Order.DoesNotExist:
                    logger.error(f"Pedido não encontrado: {external_reference}")
        
        return JsonResponse({'status': 'ok'})
        
    except Exception as e:
        logger.error(f"Erro no webhook Mercado Pago: {str(e)}")
        return JsonResponse({'status': 'error'}, status=500)


def map_mercadopago_status(mp_status):
    """Mapeia status do Mercado Pago para status interno"""
    status_map = {
        'approved': 'completed',
        'pending': 'processing',
        'in_process': 'processing',
        'rejected': 'failed',
        'cancelled': 'cancelled',
        'refunded': 'refunded'
    }
    return status_map.get(mp_status, 'pending')


def send_order_confirmation_email(order):
    """Envia email de confirmação do pedido"""
    try:
        subject = f'Pedido {order.order_number} confirmado'
        
        html_message = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'site_url': settings.SITE_URL
        })
        
        send_mail(
            subject=subject,
            message='',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False
        )
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de confirmação: {str(e)}")


@login_required
def cancel_order(request, order_id):
    """Cancela um pedido"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if not order.can_be_cancelled():
        messages.error(request, 'Este pedido não pode ser cancelado.')
        return redirect('orders:order_detail', order_id=order.id)
    
    if request.method == 'POST':
        with transaction.atomic():
            order.status = 'cancelled'
            order.save()
            
            # Devolver produtos ao estoque
            for item in order.items.all():
                item.product.increase_stock(item.quantity)
            
            messages.success(request, 'Pedido cancelado com sucesso.')
            return redirect('orders:order_detail', order_id=order.id)
    
    return render(request, 'orders/cancel_order.html', {'order': order})