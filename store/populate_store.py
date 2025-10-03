from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, Product
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo para a loja'

    def handle(self, *args, **options):
        self.stdout.write('Criando dados de exemplo...')
        
        # Criar categorias
        categories_data = [
            {
                'name': 'Eletrônicos',
                'description': 'Smartphones, tablets, notebooks e acessórios eletrônicos'
            },
            {
                'name': 'Roupas e Acessórios',
                'description': 'Roupas masculinas, femininas e acessórios de moda'
            },
            {
                'name': 'Casa e Jardim',
                'description': 'Móveis, decoração e itens para casa e jardim'
            },
            {
                'name': 'Esportes e Lazer',
                'description': 'Equipamentos esportivos e artigos de lazer'
            },
            {
                'name': 'Livros e Mídia',
                'description': 'Livros, filmes, música e jogos'
            },
            {
                'name': 'Beleza e Saúde',
                'description': 'Produtos de beleza, cuidados pessoais e saúde'
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description'],
                    'is_active': True
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Categoria criada: {category.name}')
        
        # Criar produtos
        products_data = [
            # Eletrônicos
            {
                'name': 'Smartphone Samsung Galaxy S23',
                'category': 'Eletrônicos',
                'short_description': 'Smartphone premium com câmera de 50MP e tela AMOLED',
                'description': 'O Samsung Galaxy S23 oferece performance excepcional com processador Snapdragon 8 Gen 2, câmera tripla de 50MP e tela Dynamic AMOLED de 6.1 polegadas.',
                'price': Decimal('2499.99'),
                'compare_price': Decimal('2799.99'),
                'stock_quantity': 25,
                'is_featured': True
            },
            {
                'name': 'Notebook Dell Inspiron 15',
                'category': 'Eletrônicos',
                'short_description': 'Notebook para trabalho e estudos com Intel Core i5',
                'description': 'Notebook Dell Inspiron 15 com processador Intel Core i5, 8GB RAM, SSD 256GB e tela Full HD de 15.6 polegadas.',
                'price': Decimal('2299.99'),
                'stock_quantity': 15,
                'is_featured': True
            },
            {
                'name': 'Fone de Ouvido Sony WH-1000XM4',
                'category': 'Eletrônicos',
                'short_description': 'Fone wireless com cancelamento de ruído ativo',
                'description': 'Fone de ouvido premium com tecnologia de cancelamento de ruído líder da indústria e qualidade de som excepcional.',
                'price': Decimal('899.99'),
                'compare_price': Decimal('1199.99'),
                'stock_quantity': 30
            },
            
            # Roupas e Acessórios
            {
                'name': 'Camiseta Básica Algodão',
                'category': 'Roupas e Acessórios',
                'short_description': 'Camiseta 100% algodão, confortável e versátil',
                'description': 'Camiseta básica de alta qualidade, feita em 100% algodão. Disponível em várias cores e tamanhos.',
                'price': Decimal('39.99'),
                'stock_quantity': 100,
                'is_featured': True
            },
            {
                'name': 'Jeans Masculino Slim Fit',
                'category': 'Roupas e Acessórios',
                'short_description': 'Calça jeans masculina com corte moderno',
                'description': 'Calça jeans masculina slim fit, confeccionada em denim de alta qualidade com elastano para maior conforto.',
                'price': Decimal('129.99'),
                'compare_price': Decimal('159.99'),
                'stock_quantity': 50
            },
            {
                'name': 'Tênis Esportivo Nike Air',
                'category': 'Roupas e Acessórios',
                'short_description': 'Tênis esportivo com tecnologia Air para máximo conforto',
                'description': 'Tênis esportivo Nike com tecnologia Air, ideal para corridas e atividades físicas. Design moderno e confortável.',
                'price': Decimal('299.99'),
                'stock_quantity': 40,
                'is_featured': True
            },
            
            # Casa e Jardim
            {
                'name': 'Sofá 3 Lugares Tecido',
                'category': 'Casa e Jardim',
                'short_description': 'Sofá confortável para sala de estar',
                'description': 'Sofá de 3 lugares em tecido de alta qualidade, estrutura em madeira maciça e espuma de alta densidade.',
                'price': Decimal('1299.99'),
                'compare_price': Decimal('1599.99'),
                'stock_quantity': 8
            },
            {
                'name': 'Mesa de Jantar 6 Lugares',
                'category': 'Casa e Jardim',
                'short_description': 'Mesa de jantar em madeira para 6 pessoas',
                'description': 'Mesa de jantar retangular em madeira MDF com acabamento em laminado, comporta até 6 pessoas confortavelmente.',
                'price': Decimal('899.99'),
                'stock_quantity': 12
            },
            
            # Esportes e Lazer
            {
                'name': 'Bicicleta Mountain Bike Aro 29',
                'category': 'Esportes e Lazer',
                'short_description': 'Bicicleta para trilhas e aventuras',
                'description': 'Bicicleta mountain bike com quadro em alumínio, suspensão dianteira e 21 marchas. Ideal para trilhas e uso urbano.',
                'price': Decimal('1199.99'),
                'stock_quantity': 10,
                'is_featured': True
            },
            {
                'name': 'Kit Halteres Ajustáveis',
                'category': 'Esportes e Lazer',
                'short_description': 'Kit de halteres para exercícios em casa',
                'description': 'Kit completo de halteres ajustáveis de 2kg a 20kg, ideal para treinos em casa. Inclui barras e anilhas.',
                'price': Decimal('299.99'),
                'stock_quantity': 20
            },
            
            # Livros e Mídia
            {
                'name': 'Livro: O Poder do Hábito',
                'category': 'Livros e Mídia',
                'short_description': 'Bestseller sobre como formar hábitos positivos',
                'description': 'Livro que explora a ciência por trás dos hábitos e como transformá-los para melhorar sua vida pessoal e profissional.',
                'price': Decimal('34.99'),
                'stock_quantity': 50
            },
            
            # Beleza e Saúde
            {
                'name': 'Kit Cuidados Faciais',
                'category': 'Beleza e Saúde',
                'short_description': 'Kit completo para cuidados com a pele do rosto',
                'description': 'Kit com limpador facial, tônico, hidratante e protetor solar. Ideal para rotina diária de cuidados com a pele.',
                'price': Decimal('159.99'),
                'compare_price': Decimal('199.99'),
                'stock_quantity': 35,
                'is_featured': True
            }
        ]
        
        # Criar produtos
        for prod_data in products_data:
            category = Category.objects.get(name=prod_data['category'])
            
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'slug': slugify(prod_data['name']),
                    'category': category,
                    'short_description': prod_data['short_description'],
                    'description': prod_data['description'],
                    'price': prod_data['price'],
                    'compare_price': prod_data.get('compare_price'),
                    'stock_quantity': prod_data['stock_quantity'],
                    'is_active': True,
                    'is_featured': prod_data.get('is_featured', False),
                    'track_stock': True,
                    'sku': f'SKU{random.randint(10000, 99999)}',
                    'weight': Decimal(str(random.uniform(0.1, 5.0))),
                    'meta_title': prod_data['name'],
                    'meta_description': prod_data['short_description']
                }
            )
            
            if created:
                self.stdout.write(f'Produto criado: {product.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Dados de exemplo criados com sucesso!\n'
                f'Categorias: {Category.objects.count()}\n'
                f'Produtos: {Product.objects.count()}'
            )
        )
