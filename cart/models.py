from django.db import models
from django.contrib.auth import get_user_model
from store.models import Product
from decimal import Decimal

User = get_user_model()


class Cart(models.Model):
    """Modelo para carrinho de compras persistente"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Usuário',
        null=True,
        blank=True
    )
    session_key = models.CharField(
        'Chave da Sessão',
        max_length=40,
        null=True,
        blank=True,
        help_text='Para usuários não logados'
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Carrinho'
        verbose_name_plural = 'Carrinhos'

    def __str__(self):
        if self.user:
            return f"Carrinho de {self.user.get_full_name() or self.user.username}"
        return f"Carrinho da sessão {self.session_key}"

    @property
    def total_items(self):
        """Retorna o total de itens no carrinho"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Retorna o preço total do carrinho"""
        return sum(item.get_total_price() for item in self.items.all())

    def clear(self):
        """Limpa todos os itens do carrinho"""
        self.items.all().delete()


class CartItem(models.Model):
    """Modelo para itens do carrinho"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Carrinho'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Produto'
    )
    quantity = models.PositiveIntegerField('Quantidade', default=1)
    price = models.DecimalField(
        'Preço Unitário',
        max_digits=10,
        decimal_places=2,
        help_text='Preço no momento da adição ao carrinho'
    )
    created_at = models.DateTimeField('Adicionado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens do Carrinho'
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def get_total_price(self):
        """Retorna o preço total do item (quantidade x preço)"""
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)