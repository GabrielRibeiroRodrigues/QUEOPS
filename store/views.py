from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count, Min, Max
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from .models import Product, Category, ProductImage
from decimal import Decimal


class ProductListView(ListView):
    """View para listagem de produtos com filtros e busca"""
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
        
        # Busca por texto
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(short_description__icontains=search)
            )
        
        # Filtro por categoria
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filtro por preço
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=Decimal(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=Decimal(max_price))
        
        # Ordenação
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['name', '-name', 'price', '-price', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_by)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True).annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        )
        
        # Obter range de preços para filtros
        price_range = Product.objects.filter(is_active=True).aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )
        context['price_range'] = price_range
        
        # Manter parâmetros de busca no contexto
        context['current_search'] = self.request.GET.get('search', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_min_price'] = self.request.GET.get('min_price', '')
        context['current_max_price'] = self.request.GET.get('max_price', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        
        return context


class ProductDetailView(DetailView):
    """View para detalhes do produto"""
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Produtos relacionados da mesma categoria
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(id=self.object.id).select_related('category').prefetch_related('images')[:4]
        
        return context


class CategoryDetailView(DetailView):
    """View para produtos de uma categoria específica"""
    model = Category
    template_name = 'store/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Category.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Produtos da categoria com paginação
        products = Product.objects.filter(
            category=self.object,
            is_active=True
        ).select_related('category').prefetch_related('images')
        
        # Filtros de ordenação
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['name', '-name', 'price', '-price', 'created_at', '-created_at']:
            products = products.order_by(sort_by)
        
        paginator = Paginator(products, 12)
        page_number = self.request.GET.get('page')
        context['products'] = paginator.get_page(page_number)
        context['current_sort'] = sort_by
        
        return context


def search_suggestions(request):
    """API para sugestões de busca"""
    query = request.GET.get('q', '')
    
    if len(query) >= 3:
        suggestions = Product.objects.filter(
            name__icontains=query,
            is_active=True
        ).values_list('name', flat=True)[:10]
        
        return JsonResponse({
            'suggestions': list(suggestions)
        })
    
    return JsonResponse({'suggestions': []})


# Views baseadas em função para compatibilidade
def product_list(request):
    """View de listagem de produtos"""
    view = ProductListView.as_view()
    return view(request)


def product_detail(request, slug):
    """View de detalhes do produto"""
    view = ProductDetailView.as_view()
    return view(request, slug=slug)


def category_detail(request, slug):
    """View de categoria"""
    view = CategoryDetailView.as_view()
    return view(request, slug=slug)