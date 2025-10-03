from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartDetailView.as_view(), name='cart_detail'),
    path('adicionar/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remover/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('atualizar/<int:product_id>/', views.cart_update, name='cart_update'),
    path('limpar/', views.cart_clear, name='cart_clear'),
    path('resumo/', views.cart_summary, name='cart_summary'),
]