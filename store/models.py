from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils.text import slugify
from decimal import Decimal
import os
import uuid

User = get_user_model()


def product_image_upload_path(instance, filename):
    """Gera caminho personalizado para upload de imagens de produtos"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('products', str(instance.product.id), filename)


class Category(models.Model):
    """Modelo para categorias de produtos"""
    name = models.CharField('Nome', max_length=100, unique=True)
    slug = models.SlugField('Slug', max_length=100, unique=True, blank=True)
    description = models.TextField('Descrição', blank=True, null=True)
    image = models.ImageField(
        'Imagem da Categoria',
        upload_to='categories/',
        blank=True,
        null=True,
        help_text='Imagem representativa da categoria'
    )
    is_active = models.BooleanField('Ativa', default=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',
        verbose_name='Categoria Pai'
    )
    sort_order = models.PositiveIntegerField('Ordem de Exibição', default=0)
    meta_title = models.CharField('Meta Título', max_length=60, blank=True)
    meta_description = models.CharField('Meta Descrição', max_length=160, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['is_active', 'sort_order']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:category_detail', kwargs={'slug': self.slug})

    @property
    def product_count(self):
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    """Modelo principal para produtos"""
    STOCK_STATUS_CHOICES = [
        ('in_stock', 'Em Estoque'),
        ('out_of_stock', 'Fora de Estoque'),
        ('pre_order', 'Pré-venda'),
    ]

    # Informações básicas
    name = models.CharField('Nome do Produto', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True, blank=True)
    sku = models.CharField('SKU', max_length=50, unique=True, blank=True)
    description = models.TextField('Descrição')
    short_description = models.TextField(
        'Descrição Curta',
        max_length=500,
        blank=True,
        help_text='Descrição resumida para listagens'
    )

    # Categoria e classificação
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Categoria'
    )

    # Preços
    price = models.DecimalField(
        'Preço',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    compare_price = models.DecimalField(
        'Preço de Comparação',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Preço original para mostrar desconto'
    )

    # Estoque
    stock_quantity = models.PositiveIntegerField('Quantidade em Estoque', default=0)
    stock_status = models.CharField(
        'Status do Estoque',
        max_length=20,
        choices=STOCK_STATUS_CHOICES,
        default='in_stock'
    )
    track_stock = models.BooleanField('Controlar Estoque', default=True)
    allow_backorder = models.BooleanField('Permitir Pré-venda', default=False)

    # Dimensões e peso (para cálculo de frete)
    weight = models.DecimalField(
        'Peso (kg)',
        max_digits=8,
        decimal_places=3,
        blank=True,
        null=True
    )
    length = models.DecimalField(
        'Comprimento (cm)',
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    width = models.DecimalField(
        'Largura (cm)',
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    height = models.DecimalField(
        'Altura (cm)',
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )

    # Status e controles
    is_active = models.BooleanField('Ativo', default=True)
    is_featured = models.BooleanField('Produto em Destaque', default=False)
    is_digital = models.BooleanField('Produto Digital', default=False)

    # SEO
    meta_title = models.CharField('Meta Título', max_length=60, blank=True)
    meta_description = models.CharField('Meta Descrição', max_length=160, blank=True)

    # Timestamps
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = f"PRD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    @property
    def is_on_sale(self):
        """Verifica se o produto está em promoção"""
        return self.compare_price and self.compare_price > self.price

    @property
    def discount_percentage(self):
        """Calcula o percentual de desconto"""
        if self.is_on_sale:
            return round(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0

    @property
    def is_in_stock(self):
        """Verifica se o produto está em estoque"""
        if not self.track_stock:
            return True
        return self.stock_quantity > 0 or self.allow_backorder

    def reduce_stock(self, quantity):
        """Reduz o estoque do produto"""
        if self.track_stock and self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            self.save(update_fields=['stock_quantity'])
            return True
        return False

    def increase_stock(self, quantity):
        """Aumenta o estoque do produto"""
        if self.track_stock:
            self.stock_quantity += quantity
            self.save(update_fields=['stock_quantity'])


class ProductImage(models.Model):
    """Modelo para imagens de produtos"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Produto'
    )
    image = models.ImageField('Imagem', upload_to=product_image_upload_path)
    alt_text = models.CharField(
        'Texto Alternativo',
        max_length=200,
        blank=True,
        help_text='Texto descritivo da imagem para acessibilidade'
    )
    is_primary = models.BooleanField('Imagem Principal', default=False)
    sort_order = models.PositiveIntegerField('Ordem', default=0)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Imagem do Produto'
        verbose_name_plural = 'Imagens dos Produtos'
        ordering = ['sort_order', 'created_at']

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Remove a flag primary de outras imagens do mesmo produto
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - Imagem {self.sort_order}"