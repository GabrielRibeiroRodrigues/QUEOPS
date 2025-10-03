import mercadopago
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class MercadoPagoService:
    """
    Serviço para integração com a API do Mercado Pago.
    """
    
    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    
    def create_preference(self, order):
        """
        Cria uma preferência de pagamento no Mercado Pago.
        
        Args:
            order: Instância do modelo Order
            
        Returns:
            dict: Resposta da API do Mercado Pago
        """
        try:
            # Preparar itens do pedido
            items = []
            for item in order.items.all():
                items.append({
                    "title": item.product_name,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "currency_id": "BRL"
                })
            
            # Configurar dados da preferência
            preference_data = {
                "items": items,
                "payer": {
                    "name": order.user.first_name,
                    "surname": order.user.last_name,
                    "email": order.user.email,
                    "phone": {
                        "number": order.user.phone_number or ""
                    },
                    "address": {
                        "street_name": order.shipping_address_line_1,
                        "street_number": "",
                        "zip_code": order.shipping_postal_code
                    }
                },
                "back_urls": {
                    "success": f"{settings.SITE_URL}/pedidos/{order.id}/sucesso/",
                    "failure": f"{settings.SITE_URL}/pedidos/{order.id}/falha/",
                    "pending": f"{settings.SITE_URL}/pedidos/{order.id}/pendente/"
                },
                "auto_return": "approved",
                "external_reference": str(order.id),
                "notification_url": f"{settings.SITE_URL}/webhooks/mercadopago/",
                "statement_descriptor": "ECOMMERCE",
                "payment_methods": {
                    "excluded_payment_methods": [],
                    "excluded_payment_types": [],
                    "installments": 12
                },
                "shipments": {
                    "cost": float(order.shipping_cost),
                    "mode": "not_specified"
                }
            }
            
            # Criar preferência
            preference_response = self.sdk.preference().create(preference_data)
            
            if preference_response["status"] == 201:
                logger.info(f"Preferência criada com sucesso para o pedido {order.id}")
                return {
                    "success": True,
                    "preference_id": preference_response["response"]["id"],
                    "init_point": preference_response["response"]["init_point"],
                    "sandbox_init_point": preference_response["response"]["sandbox_init_point"]
                }
            else:
                logger.error(f"Erro ao criar preferência: {preference_response}")
                return {
                    "success": False,
                    "error": preference_response.get("message", "Erro desconhecido")
                }
                
        except Exception as e:
            logger.error(f"Erro na integração com Mercado Pago: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_payment_info(self, payment_id):
        """
        Obtém informações de um pagamento específico.
        
        Args:
            payment_id: ID do pagamento no Mercado Pago
            
        Returns:
            dict: Informações do pagamento
        """
        try:
            payment_response = self.sdk.payment().get(payment_id)
            
            if payment_response["status"] == 200:
                return {
                    "success": True,
                    "payment": payment_response["response"]
                }
            else:
                return {
                    "success": False,
                    "error": "Pagamento não encontrado"
                }
                
        except Exception as e:
            logger.error(f"Erro ao buscar pagamento {payment_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_webhook(self, data):
        """
        Processa webhook do Mercado Pago.
        
        Args:
            data: Dados do webhook
            
        Returns:
            dict: Resultado do processamento
        """
        try:
            if data.get("type") == "payment":
                payment_id = data.get("data", {}).get("id")
                
                if payment_id:
                    payment_info = self.get_payment_info(payment_id)
                    
                    if payment_info["success"]:
                        payment = payment_info["payment"]
                        external_reference = payment.get("external_reference")
                        
                        if external_reference:
                            # Atualizar status do pedido
                            from .models import Order, Payment
                            
                            try:
                                order = Order.objects.get(id=external_reference)
                                
                                # Criar ou atualizar pagamento
                                payment_obj, created = Payment.objects.get_or_create(
                                    order=order,
                                    gateway_transaction_id=str(payment_id),
                                    defaults={
                                        "payment_method": "mercadopago",
                                        "amount": Decimal(str(payment["transaction_amount"])),
                                        "gateway_response": payment
                                    }
                                )
                                
                                # Atualizar status baseado no status do pagamento
                                if payment["status"] == "approved":
                                    payment_obj.status = "completed"
                                    order.payment_status = "paid"
                                    order.status = "processing"
                                elif payment["status"] == "pending":
                                    payment_obj.status = "pending"
                                    order.payment_status = "pending"
                                elif payment["status"] in ["cancelled", "rejected"]:
                                    payment_obj.status = "failed"
                                    order.payment_status = "failed"
                                
                                payment_obj.gateway_response = payment
                                payment_obj.save()
                                order.save()
                                
                                logger.info(f"Webhook processado para pedido {order.id}")
                                
                                return {
                                    "success": True,
                                    "message": "Webhook processado com sucesso"
                                }
                                
                            except Order.DoesNotExist:
                                logger.error(f"Pedido não encontrado: {external_reference}")
                                return {
                                    "success": False,
                                    "error": "Pedido não encontrado"
                                }
            
            return {
                "success": True,
                "message": "Webhook ignorado"
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class FreteService:
    """
    Serviço para cálculo de frete via API dos Correios.
    """
    
    def __init__(self):
        self.base_url = "https://ws.correios.com.br/calculador/v1/calcular-preco-prazo"
        self.user = settings.CORREIOS_USER
        self.password = settings.CORREIOS_PASSWORD
    
    def calculate_shipping(self, cep_destino, peso, comprimento, altura, largura, valor_declarado=0):
        """
        Calcula o frete para um CEP de destino.
        
        Args:
            cep_destino: CEP de destino
            peso: Peso em kg
            comprimento: Comprimento em cm
            altura: Altura em cm
            largura: Largura em cm
            valor_declarado: Valor declarado para seguro
            
        Returns:
            dict: Opções de frete disponíveis
        """
        import requests
        
        try:
            # CEP de origem (configurável)
            cep_origem = getattr(settings, 'CORREIOS_CEP_ORIGEM', '01310-100')
            
            # Serviços dos Correios
            servicos = [
                '04014',  # SEDEX
                '04510',  # PAC
                '04782',  # SEDEX 12
            ]
            
            opcoes_frete = []
            
            for servico in servicos:
                params = {
                    'cepOrigem': cep_origem,
                    'cepDestino': cep_destino,
                    'peso': peso,
                    'comprimento': comprimento,
                    'altura': altura,
                    'largura': largura,
                    'servico': servico,
                    'valorDeclarado': valor_declarado
                }
                
                # Fazer requisição para API dos Correios
                # Nota: Esta é uma implementação simplificada
                # Em produção, usar a API oficial dos Correios
                
                # Simulação de resposta para desenvolvimento
                if servico == '04014':  # SEDEX
                    opcoes_frete.append({
                        'servico': 'SEDEX',
                        'codigo': '04014',
                        'valor': 25.50,
                        'prazo': '1-2 dias úteis',
                        'erro': None
                    })
                elif servico == '04510':  # PAC
                    opcoes_frete.append({
                        'servico': 'PAC',
                        'codigo': '04510',
                        'valor': 15.80,
                        'prazo': '3-5 dias úteis',
                        'erro': None
                    })
                elif servico == '04782':  # SEDEX 12
                    opcoes_frete.append({
                        'servico': 'SEDEX 12',
                        'codigo': '04782',
                        'valor': 35.90,
                        'prazo': 'Até 12h do próximo dia útil',
                        'erro': None
                    })
            
            return {
                "success": True,
                "opcoes": opcoes_frete
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular frete: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "opcoes": []
            }
    
    def calculate_cart_shipping(self, cart, cep_destino):
        """
        Calcula o frete para todos os itens do carrinho.
        
        Args:
            cart: Instância do carrinho
            cep_destino: CEP de destino
            
        Returns:
            dict: Opções de frete para o carrinho
        """
        try:
            # Calcular peso e dimensões totais
            peso_total = 0
            comprimento_max = 0
            altura_max = 0
            largura_max = 0
            valor_total = 0
            
            for item in cart:
                produto = item['product']
                quantidade = item['quantity']
                
                # Somar peso
                if produto.weight:
                    peso_total += float(produto.weight) * quantidade
                
                # Dimensões máximas
                if produto.dimensions_length:
                    comprimento_max = max(comprimento_max, float(produto.dimensions_length))
                if produto.dimensions_height:
                    altura_max = max(altura_max, float(produto.dimensions_height))
                if produto.dimensions_width:
                    largura_max = max(largura_max, float(produto.dimensions_width))
                
                # Valor total
                valor_total += float(item['total_price'])
            
            # Valores mínimos para cálculo
            peso_total = max(peso_total, 0.1)  # Mínimo 100g
            comprimento_max = max(comprimento_max, 16)  # Mínimo 16cm
            altura_max = max(altura_max, 2)  # Mínimo 2cm
            largura_max = max(largura_max, 11)  # Mínimo 11cm
            
            return self.calculate_shipping(
                cep_destino=cep_destino,
                peso=peso_total,
                comprimento=comprimento_max,
                altura=altura_max,
                largura=largura_max,
                valor_declarado=valor_total
            )
            
        except Exception as e:
            logger.error(f"Erro ao calcular frete do carrinho: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "opcoes": []
            }
