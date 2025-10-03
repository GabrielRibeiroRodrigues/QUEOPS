from django.core.management.base import BaseCommand
from django.db import transaction
from store.models import Category, Product, ProductImage
from decimal import Decimal
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import requests
import os


class Command(BaseCommand):
    help = 'Popula o banco de dados com produtos de exemplo'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('Criando categorias...')
            self.create_categories()
            
            self.stdout.write('Criando produtos...')
            self.create_products()
            
            self.stdout.write(
                self.style.SUCCESS('Banco de dados populado com sucesso!')
            )

    def create_categories(self):
        categories_data = [
            {
                'name': 'Eletrônicos',
                'description': 'Smartphones, tablets, notebooks e acessórios'
            },
            {
                'name': 'Roupas e Acessórios',
                'description': 'Roupas masculinas, femininas e acessórios'
            },
            {
                'name': 'Casa e Jardim',
                'description': 'Produtos para casa, decoração e jardim'
            },
            {
                'name': 'Esportes e Lazer',
                'description': 'Equipamentos esportivos e produtos de lazer'
            },
            {
                'name': 'Livros e Educação',
                'description': 'Livros, material escolar e educacional'
            },
            {
                'name': 'Saúde e Beleza',
                'description': 'Produtos de saúde, beleza e bem-estar'
            }
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Categoria "{category.name}" criada')

    def create_products(self):
        # Obter categorias
        try:
            eletronicos = Category.objects.get(name='Eletrônicos')
            roupas = Category.objects.get(name='Roupas e Acessórios')
            casa = Category.objects.get(name='Casa e Jardim')
            esportes = Category.objects.get(name='Esportes e Lazer')
            livros = Category.objects.get(name='Livros e Educação')
            saude = Category.objects.get(name='Saúde e Beleza')
        except Category.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Erro: Categorias não encontradas!')
            )
            return

        products_data = [
            # Eletrônicos
            {
                'name': 'Smartphone Samsung Galaxy S23',
                'category': eletronicos,
                'short_description': 'Smartphone top de linha com câmera de 50MP',
                'description': 'O Samsung Galaxy S23 oferece performance excepcional com processador Snapdragon 8 Gen 2, câmera tripla de 50MP e tela Dynamic AMOLED de 6.1 polegadas.',
                'price': Decimal('2499.99'),
                'compare_price': Decimal('2799.99'),
                'stock_quantity': 25,
                'is_featured': True,
                'weight': Decimal('0.168'),
                'length': Decimal('14.6'),
                'width': Decimal('7.1'),
                'height': Decimal('0.8')
            },
            {
                'name': 'Notebook Dell Inspiron 15',
                'category': eletronicos,
                'short_description': 'Notebook para trabalho e estudos com Intel Core i5',
                'description': 'Notebook Dell Inspiron 15 com processador Intel Core i5, 8GB RAM, SSD 256GB e tela Full HD de 15.6 polegadas.',
                'price': Decimal('2299.99'),
                'stock_quantity': 15,
                'is_featured': True,
                'weight': Decimal('1.8'),
                'length': Decimal('35.6'),
                'width': Decimal('23.5'),
                'height': Decimal('1.8')
            },
            {
                'name': 'Fone de Ouvido Bluetooth Sony WH-1000XM4',
                'category': eletronicos,
                'short_description': 'Fone com cancelamento de ruído ativo',
                'description': 'Fone de ouvido premium com cancelamento de ruído líder da indústria, áudio de alta qualidade e bateria de até 30 horas.',
                'price': Decimal('899.99'),
                'compare_price': Decimal('1199.99'),
                'stock_quantity': 40,
                'weight': Decimal('0.254'),
                'length': Decimal('25.4'),
                'width': Decimal('20.3'),
                'height': Decimal('7.6')
            },
            
            # Roupas e Acessórios
            {
                'name': 'Camiseta Polo Ralph Lauren',
                'category': roupas,
                'short_description': 'Camiseta polo clássica de algodão',
                'description': 'Camiseta polo clássica Ralph Lauren feita em 100% algodão pima, com ajuste regular e logo bordado.',
                'price': Decimal('189.99'),
                'compare_price': Decimal('229.99'),
                'stock_quantity': 60,
                'weight': Decimal('0.2'),
                'length': Decimal('30'),
                'width': Decimal('25'),
                'height': Decimal('2')
            },
            {
                'name': 'Tênis Nike Air Max 270',
                'category': roupas,
                'short_description': 'Tênis esportivo com tecnologia Air Max',
                'description': 'Tênis Nike Air Max 270 com unidade Air Max visível no calcanhar, proporcionando conforto e estilo únicos.',
                'price': Decimal('499.99'),
                'stock_quantity': 35,
                'is_featured': True,
                'weight': Decimal('0.8'),
                'length': Decimal('32'),
                'width': Decimal('22'),
                'height': Decimal('12')
            },
            
            # Casa e Jardim
            {
                'name': 'Cafeteira Nespresso Essenza Mini',
                'category': casa,
                'short_description': 'Cafeteira compacta para cápsulas Nespresso',
                'description': 'Cafeteira Nespresso Essenza Mini, design compacto, preparo rápido de café espresso e lungo.',
                'price': Decimal('299.99'),
                'stock_quantity': 20,
                'weight': Decimal('2.3'),
                'length': Decimal('32.5'),
                'width': Decimal('11'),
                'height': Decimal('20.5')
            },
            {
                'name': 'Conjunto de Panelas Tramontina',
                'category': casa,
                'short_description': 'Conjunto com 5 panelas antiaderentes',
                'description': 'Conjunto de panelas Tramontina com revestimento antiaderente, cabo anatômico e fundo triplo.',
                'price': Decimal('249.99'),
                'compare_price': Decimal('349.99'),
                'stock_quantity': 25,
                'weight': Decimal('3.5'),
                'length': Decimal('40'),
                'width': Decimal('25'),
                'height': Decimal('20')
            },
            
            # Esportes e Lazer
            {
                'name': 'Bicicleta Mountain Bike Caloi',
                'category': esportes,
                'short_description': 'Mountain bike com 21 marchas',
                'description': 'Bicicleta mountain bike Caloi com quadro de alumínio, 21 marchas Shimano e freios V-brake.',
                'price': Decimal('899.99'),
                'stock_quantity': 10,
                'is_featured': True,
                'weight': Decimal('15'),
                'length': Decimal('170'),
                'width': Decimal('60'),
                'height': Decimal('100')
            },
            {
                'name': 'Kit de Musculação Doméstica',
                'category': esportes,
                'short_description': 'Kit completo para exercícios em casa',
                'description': 'Kit de musculação com halteres ajustáveis, barras, anilhas e suporte, ideal para treinos em casa.',
                'price': Decimal('599.99'),
                'stock_quantity': 15,
                'weight': Decimal('25'),
                'length': Decimal('60'),
                'width': Decimal('40'),
                'height': Decimal('30')
            },
            
            # Livros e Educação
            {
                'name': 'Livro: "Clean Code" - Robert C. Martin',
                'category': livros,
                'short_description': 'Manual de boas práticas de programação',
                'description': 'Livro essencial sobre desenvolvimento de software limpo e boas práticas de programação.',
                'price': Decimal('89.99'),
                'stock_quantity': 50,
                'weight': Decimal('0.6'),
                'length': Decimal('23'),
                'width': Decimal('15'),
                'height': Decimal('3')
            },
            {
                'name': 'Curso Online: Python para Iniciantes',
                'category': livros,
                'short_description': 'Curso completo de Python do básico ao avançado',
                'description': 'Curso online completo de Python com certificado, projetos práticos e suporte do instrutor.',
                'price': Decimal('197.99'),
                'compare_price': Decimal('297.99'),
                'stock_quantity': 999,
                'is_digital': True,
                'track_stock': False
            },
            
            # Saúde e Beleza
            {
                'name': 'Protetor Solar Facial FPS 60',
                'category': saude,
                'short_description': 'Proteção solar facial com FPS 60',
                'description': 'Protetor solar facial com FPS 60, textura leve, absorção rápida e proteção UVA/UVB.',
                'price': Decimal('45.99'),
                'stock_quantity': 80,
                'weight': Decimal('0.05'),
                'length': Decimal('15'),
                'width': Decimal('5'),
                'height': Decimal('3')
            },
            {
                'name': 'Vitamina C + Zinco - 60 cápsulas',
                'category': saude,
                'short_description': 'Suplemento vitamínico para imunidade',
                'description': 'Vitamina C com Zinco para fortalecimento do sistema imunológico, 60 cápsulas.',
                'price': Decimal('29.99'),
                'stock_quantity': 100,
                'weight': Decimal('0.1'),
                'length': Decimal('10'),
                'width': Decimal('6'),
                'height': Decimal('6')
            }
        ]
        
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                self.stdout.write(f'  ✓ Produto "{product.name}" criado')
                
                # Adicionar imagem placeholder se não existir
                if not product.images.exists():
                    # Criar uma imagem placeholder simples
                    try:
                        # Para ambiente de desenvolvimento, não vamos baixar imagens reais
                        # Apenas criar o produto sem imagem ou com placeholder local
                        pass
                    except Exception as e:
                        self.stdout.write(f'    ⚠ Não foi possível criar imagem para {product.name}: {e}')