from django.shortcuts import render


def home(request):
    """
    View da página inicial.
    """
    try:
        from store.models import Product, Category
        
        # Produtos em destaque
        featured_products = Product.objects.filter(
            is_active=True, 
            is_featured=True
        ).select_related('category').prefetch_related('images')[:8]
        
        # Produtos mais recentes
        latest_products = Product.objects.filter(
            is_active=True
        ).select_related('category').prefetch_related('images').order_by('-created_at')[:8]
        
        # Categorias ativas
        categories = Category.objects.filter(is_active=True)[:6]
        
    except Exception as e:
        # Se houver erro com os modelos, usar dados vazios
        featured_products = []
        latest_products = []
        categories = []
    
    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'categories': categories,
    }
    
    return render(request, 'home_temp.html', context)


def about(request):
    """
    View da página sobre.
    """
    return render(request, 'core/about.html')


def contact(request):
    """
    View da página de contato.
    """
    return render(request, 'core/contact.html')
