from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('produto/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('categoria/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('busca-sugestoes/', views.search_suggestions, name='search_suggestions'),
]