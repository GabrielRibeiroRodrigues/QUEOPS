from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Listagem e detalhes de pedidos
    path('', views.OrderListView.as_view(), name='order_list'),
    path('<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    
    # Processo de checkout
    path('checkout/', views.checkout, name='checkout'),
    
    # Pagamento
    path('<int:order_id>/payment/', views.payment, name='payment'),
    path('<int:order_id>/create-payment/', views.create_payment, name='create_payment'),
    path('<int:order_id>/payment-success/', views.payment_success, name='payment_success'),
    path('<int:order_id>/payment-failure/', views.payment_failure, name='payment_failure'),
    path('<int:order_id>/payment-pending/', views.payment_pending, name='payment_pending'),
    
    # Cancelamento
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    
    # Webhook do Mercado Pago
    path('webhook/mercadopago/', views.mercadopago_webhook, name='mercadopago_webhook'),
]