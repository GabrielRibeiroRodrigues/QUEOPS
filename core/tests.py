from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Category, Product, ProductImage

User = get_user_model()


class CategoryModelTest(TestCase):
    """
    Testes para o modelo Category.
    """
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Eletrônicos',
            slug='eletronicos',
            description='Produtos eletrônicos',
            is_active=True
        )
    
    def test_category_creation(self):
        """Testa a criação de uma categoria."""
        self.assertEqual(self.category.name, 'Eletrônicos')
        self.assertEqual(self.category.slug, 'eletronicos')
        self.assertTrue(self.category.is_active)
    
    def test_category_str(self):
        """Testa a representação string da categoria."""
        self.assertEqual(str(self.category), 'Eletrônicos')
    
    def test_category_get_absolute_url(self):
        """Testa a URL absoluta da categoria."""
        expected_url = reverse('store:category_detail', kwargs={'slug': 'eletronicos'})
        self.assertEqual(self.category.get_absolute_url(), expected_url)


class ProductModelTest(TestCase):
    """
    Testes para o modelo Product.
    """
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Eletrônicos',
            slug='eletronicos',
            description='Produtos eletrônicos',
            is_active=True
        )
        
        self.product = Product.objects.create(
            name='Smartphone',
            slug='smartphone',
            category=self.category,
            description='Uma descrição do smartphone',
            short_description='Smartphone moderno',
            price=Decimal('999.99'),
            compare_price=Decimal('1199.99'),
            stock_quantity=10,
            is_active=True,
            is_featured=True,
            track_stock=True,
            sku='SMART001'
        )
    
    def test_product_creation(self):
        """Testa a criação de um produto."""
        self.assertEqual(self.product.name, 'Smartphone')
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.price, Decimal('999.99'))
        self.assertTrue(self.product.is_active)
    
    def test_product_str(self):
        """Testa a representação string do produto."""
        self.assertEqual(str(self.product), 'Smartphone')
    
    def test_product_get_absolute_url(self):
        """Testa a URL absoluta do produto."""
        expected_url = reverse('store:product_detail', kwargs={'slug': 'smartphone'})
        self.assertEqual(self.product.get_absolute_url(), expected_url)
    
    def test_product_discount_percentage(self):
        """Testa o cálculo da porcentagem de desconto."""
        discount = self.product.get_discount_percentage()
        expected_discount = round(((Decimal('1199.99') - Decimal('999.99')) / Decimal('1199.99')) * 100)
        self.assertEqual(discount, expected_discount)
    
    def test_product_can_be_purchased(self):
        """Testa se o produto pode ser comprado."""
        self.assertTrue(self.product.can_be_purchased())
        
        # Produto sem estoque
        self.product.stock_quantity = 0
        self.product.save()
        self.assertFalse(self.product.can_be_purchased())
        
        # Produto inativo
        self.product.stock_quantity = 10
        self.product.is_active = False
        self.product.save()
        self.assertFalse(self.product.can_be_purchased())


class StoreViewsTest(TestCase):
    """
    Testes para as views da loja.
    """
    
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name='Eletrônicos',
            slug='eletronicos',
            description='Produtos eletrônicos',
            is_active=True
        )
        
        self.product = Product.objects.create(
            name='Smartphone',
            slug='smartphone',
            category=self.category,
            description='Uma descrição do smartphone',
            short_description='Smartphone moderno',
            price=Decimal('999.99'),
            stock_quantity=10,
            is_active=True,
            sku='SMART001'
        )
    
    def test_product_list_view(self):
        """Testa a view de listagem de produtos."""
        url = reverse('store:product_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smartphone')
        self.assertContains(response, 'Eletrônicos')
    
    def test_product_detail_view(self):
        """Testa a view de detalhes do produto."""
        url = reverse('store:product_detail', kwargs={'slug': 'smartphone'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smartphone')
        self.assertContains(response, 'R$ 999.99')
    
    def test_category_detail_view(self):
        """Testa a view de detalhes da categoria."""
        url = reverse('store:category_detail', kwargs={'slug': 'eletronicos'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Eletrônicos')
        self.assertContains(response, 'Smartphone')
    
    def test_product_search_view(self):
        """Testa a view de busca de produtos."""
        url = reverse('store:product_search')
        response = self.client.get(url, {'q': 'smartphone'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smartphone')
        
        # Busca sem resultados
        response = self.client.get(url, {'q': 'produto inexistente'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Smartphone')


class ProductImageTest(TestCase):
    """
    Testes para o modelo ProductImage.
    """
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Eletrônicos',
            slug='eletronicos',
            description='Produtos eletrônicos',
            is_active=True
        )
        
        self.product = Product.objects.create(
            name='Smartphone',
            slug='smartphone',
            category=self.category,
            description='Uma descrição do smartphone',
            short_description='Smartphone moderno',
            price=Decimal('999.99'),
            stock_quantity=10,
            is_active=True,
            sku='SMART001'
        )
    
    def test_product_main_image(self):
        """Testa a imagem principal do produto."""
        # Produto sem imagens
        self.assertIsNone(self.product.get_main_image())
        
        # Adicionar imagem
        image = ProductImage.objects.create(
            product=self.product,
            alt_text='Smartphone frontal',
            is_main=True
        )
        
        self.assertEqual(self.product.get_main_image(), image)
