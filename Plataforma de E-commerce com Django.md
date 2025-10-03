# Plataforma de E-commerce com Django

Este projeto é uma plataforma de e-commerce robusta, segura e escalável, desenvolvida com o framework Django (Python) e Bootstrap 5 para o frontend. Ele foi projetado para atender a requisitos funcionais e não funcionais detalhados, oferecendo gerenciamento de produtos, carrinho de compras, checkout com pagamento online e área do cliente.

## Funcionalidades Implementadas (Fase Inicial)

- **Gerenciamento de Usuários:** Modelo de usuário customizado com campos adicionais (telefone, CPF, endereço) e integração com o Django Admin.
- **Catálogo de Produtos:** Modelos para `Category`, `Product` e `ProductImage` com campos detalhados, slugs automáticos, controle de estoque e otimização de imagens. Configuração completa no Django Admin para CRUD.
- **Carrinho de Compras:** Lógica de carrinho baseada em sessões, com adição, remoção e atualização de produtos.
- **Pedidos:** Modelos para `Order`, `OrderItem` e `Payment` para gerenciar o fluxo de pedidos e pagamentos. Configuração completa no Django Admin.
- **Páginas Estáticas:** Páginas de Início, Sobre e Contato com layout responsivo usando Bootstrap 5.
- **Configuração Inicial:** Ambiente de desenvolvimento configurado com `requirements.txt`, `.env` para variáveis de ambiente e `settings.py` otimizado.

## Tecnologias Utilizadas

- **Backend:** Python 3.11+ com Django 5.x
- **Banco de Dados:** PostgreSQL (produção), SQLite (desenvolvimento)
- **Frontend:** Bootstrap 5, HTML, CSS, JavaScript
- **Cache:** Redis (configurado, mas a implementação de uso ainda será detalhada)
- **Pagamentos:** Mercado Pago (integração planejada)
- **Frete:** Correios (integração planejada)
- **Testes:** Pytest, Pytest-Django (planejado)
- **Containerização:** Docker, Docker Compose (configuração inicial)

## Configuração do Ambiente de Desenvolvimento

Siga os passos abaixo para configurar e rodar o projeto localmente.

### 1. Pré-requisitos

Certifique-se de ter instalado:
- Python 3.11 ou superior
- `pip` (gerenciador de pacotes Python)
- `git` (para clonar o repositório)
- Docker e Docker Compose (opcional, para ambiente containerizado)

### 2. Clonar o Repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd ecommerce-platform
```

### 3. Configurar Ambiente Virtual

É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto.

```bash
python3.11 -m venv venv
source venv/bin/activate  # No Windows: .\venv\Scripts\activate
```

### 4. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 5. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (`ecommerce-platform/.env`) e preencha com as variáveis necessárias. Um exemplo (`.env.example`) pode ser fornecido, mas você deve criar o seu próprio.

```ini
# Exemplo de .env
SECRET_KEY=sua_chave_secreta_aqui_e_muito_importante
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/1
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
MERCADOPAGO_ACCESS_TOKEN=seu_token_aqui
MERCADOPAGO_PUBLIC_KEY=sua_chave_publica_aqui
CORREIOS_USER=seu_usuario_correios
CORREIOS_PASSWORD=sua_senha_correios
MEDIA_ROOT=/home/ubuntu/ecommerce-platform/media
STATIC_ROOT=/home/ubuntu/ecommerce-platform/staticfiles
```

**Importante:** A `SECRET_KEY` deve ser uma string longa e aleatória. Nunca a exponha em repositórios públicos.

### 6. Migrações do Banco de Dados

Aplique as migrações para criar as tabelas no banco de dados.

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Criar Superusuário (para acessar o Django Admin)

```bash
python manage.py createsuperuser
# Siga as instruções para criar o usuário (ex: username=admin, email=admin@example.com, password=admin123)
```

### 8. Coletar Arquivos Estáticos

```bash
python manage.py collectstatic
```

### 9. Rodar o Servidor de Desenvolvimento

```bash
python manage.py runserver
```

O site estará disponível em `http://127.0.0.1:8000/` e o painel administrativo em `http://127.0.0.1:8000/admin/`.

## Configuração Docker (Em Breve)

Serão fornecidos `Dockerfile` e `docker-compose.yml` para facilitar a containerização e o deploy do projeto em ambientes de produção e desenvolvimento. Esta etapa será detalhada em uma fase posterior do projeto.
