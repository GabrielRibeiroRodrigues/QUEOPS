from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from store.models import Product
from decimal import Decimal
import uuid

User = get_user_model()


class Order(models.Model):
    """Modelo principal para pedidos"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmado'),
        ('processing', 'Processando'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregue'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
    ]

    # Identificação
    order_number = models.CharField('Número do Pedido', max_length=50, unique=True, blank=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Cliente',
        null=True,
        blank=True
    )

    # Status
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(
        'Status do Pagamento',
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )

    # Informações do cliente
    email = models.EmailField('E-mail')
    first_name = models.CharField('Nome', max_length=50)
    last_name = models.CharField('Sobrenome', max_length=50)
    phone = models.CharField('Telefone', max_length=20, blank=True)

    # Endereço de entrega
    shipping_address_line_1 = models.CharField('Endereço', max_length=255)
    shipping_address_line_2 = models.CharField('Complemento', max_length=255, blank=True)
    shipping_city = models.CharField('Cidade', max_length=100)
    shipping_state = models.CharField('Estado', max_length=2)
    shipping_postal_code = models.CharField('CEP', max_length=9)
    shipping_country = models.CharField('País', max_length=50, default='Brasil')

    # Endereço de cobrança (opcional, pode ser igual ao de entrega)
    billing_same_as_shipping = models.BooleanField('Cobrança igual à entrega', default=True)
    billing_address_line_1 = models.CharField('Endereço de Cobrança', max_length=255, blank=True)
    billing_address_line_2 = models.CharField('Complemento de Cobrança', max_length=255, blank=True)
    billing_city = models.CharField('Cidade de Cobrança', max_length=100, blank=True)
    billing_state = models.CharField('Estado de Cobrança', max_length=2, blank=True)
    billing_postal_code = models.CharField('CEP de Cobrança', max_length=9, blank=True)
    billing_country = models.CharField('País de Cobrança', max_length=50, default='Brasil', blank=True)

    # Valores
    subtotal = models.DecimalField(
        'Subtotal',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    shipping_cost = models.DecimalField(
        'Custo do Frete',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    tax_amount = models.DecimalField(
        'Impostos',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_amount = models.DecimalField(
        'Desconto',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total = models.DecimalField(
        'Total',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Informações de entrega
    shipping_method = models.CharField('Método de Entrega', max_length=100, blank=True)
    tracking_number = models.CharField('Código de Rastreamento', max_length=100, blank=True)

    # Observações
    notes = models.TextField('Observações', blank=True)

    # Timestamps
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    shipped_at = models.DateTimeField('Enviado em', null=True, blank=True)
    delivered_at = models.DateTimeField('Entregue em', null=True, blank=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'payment_status']),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Gera um número único para o pedido"""
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"

    def __str__(self):
        return f"Pedido {self.order_number}"

    @property
    def full_name(self):
        """Retorna o nome completo do cliente"""
        return f"{self.first_name} {self.last_name}"

    @property
    def shipping_address(self):
        """Retorna o endereço de entrega formatado"""
        address_parts = [
            self.shipping_address_line_1,
            self.shipping_address_line_2,
            self.shipping_city,
            self.shipping_state,
            self.shipping_postal_code
        ]
        return ', '.join([part for part in address_parts if part])

    def can_be_cancelled(self):
        """Verifica se o pedido pode ser cancelado"""
        return self.status in ['pending', 'confirmed']

    def get_total_items(self):
        """Retorna o total de itens no pedido"""
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """Modelo para itens do pedido"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Pedido'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Produto'
    )
    product_name = models.CharField(
        'Nome do Produto',
        max_length=200,
        help_text='Nome do produto no momento da compra'
    )
    product_sku = models.CharField(
        'SKU do Produto',
        max_length=50,
        blank=True,
        help_text='SKU do produto no momento da compra'
    )
    quantity = models.PositiveIntegerField('Quantidade')
    unit_price = models.DecimalField(
        'Preço Unitário',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    total_price = models.DecimalField(
        'Preço Total',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def save(self, *args, **kwargs):
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_sku:
            self.product_sku = self.product.sku
        if not self.total_price:
            self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"


class Payment(models.Model):
    """Modelo para pagamentos"""
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto Bancário'),
        ('bank_transfer', 'Transferência Bancária'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Pedido'
    )
    payment_id = models.CharField('ID do Pagamento', max_length=100, unique=True, blank=True)
    payment_method = models.CharField(
        'Método de Pagamento',
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(
        'Valor',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Dados do gateway de pagamento
    gateway = models.CharField('Gateway', max_length=50, blank=True)
    gateway_transaction_id = models.CharField('ID da Transação no Gateway', max_length=100, blank=True)
    gateway_response = models.JSONField('Resposta do Gateway', blank=True, null=True)

    # Informações adicionais
    installments = models.PositiveIntegerField('Parcelas', default=1)
    due_date = models.DateTimeField('Data de Vencimento', null=True, blank=True)
    paid_at = models.DateTimeField('Pago em', null=True, blank=True)

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pagamento {self.payment_id} - {self.get_payment_method_display()}"


class ShippingRate(models.Model):
    """Modelo para tarifas de frete"""
    name = models.CharField('Nome do Serviço', max_length=100)
    carrier = models.CharField('Transportadora', max_length=100)
    min_weight = models.DecimalField(
        'Peso Mínimo (kg)',
        max_digits=8,
        decimal_places=3,
        default=Decimal('0.000')
    )
    max_weight = models.DecimalField(
        'Peso Máximo (kg)',
        max_digits=8,
        decimal_places=3,
        default=Decimal('30.000')
    )
    base_price = models.DecimalField(
        'Preço Base',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    price_per_kg = models.DecimalField(
        'Preço por Kg Adicional',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    delivery_time = models.PositiveIntegerField('Prazo de Entrega (dias)', default=7)
    is_active = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Tarifa de Frete'
        verbose_name_plural = 'Tarifas de Frete'
        ordering = ['delivery_time', 'base_price']

    def __str__(self):
        return f"{self.carrier} - {self.name}"

    def calculate_shipping_cost(self, weight):
        """Calcula o custo do frete baseado no peso"""
        if weight <= self.min_weight:
            return self.base_price
        
        additional_weight = weight - self.min_weight
        additional_cost = additional_weight * self.price_per_kg
        return self.base_price + additional_cost