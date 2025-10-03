from decimal import Decimal
from django.conf import settings
from store.models import Product


class Cart:
    """
    Classe para gerenciar o carrinho de compras baseado em sessões.
    """
    
    def __init__(self, request):
        """
        Inicializa o carrinho.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Salva um carrinho vazio na sessão
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Adiciona um produto ao carrinho ou atualiza sua quantidade.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        self.save()

    def save(self):
        """
        Marca a sessão como "modificada" para garantir que seja salva.
        """
        self.session.modified = True

    def remove(self, product):
        """
        Remove um produto do carrinho.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Itera sobre os itens do carrinho e obtém os produtos do banco de dados.
        """
        product_ids = self.cart.keys()
        # Obtém os objetos produto e os adiciona ao carrinho
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Conta todos os itens no carrinho.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Calcula o preço total dos itens no carrinho.
        """
        return sum(
            Decimal(item['price']) * item['quantity'] 
            for item in self.cart.values()
        )

    def clear(self):
        """
        Remove o carrinho da sessão.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def get_item_count(self):
        """
        Retorna o número total de itens no carrinho.
        """
        return len(self)

    def get_item(self, product):
        """
        Retorna um item específico do carrinho.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            item = self.cart[product_id].copy()
            item['product'] = product
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            return item
        return None

    def update_quantity(self, product, quantity):
        """
        Atualiza a quantidade de um produto no carrinho.
        """
        if quantity > 0:
            self.add(product, quantity, override_quantity=True)
        else:
            self.remove(product)
