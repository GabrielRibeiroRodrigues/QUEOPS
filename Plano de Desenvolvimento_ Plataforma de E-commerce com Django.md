# Plano de Desenvolvimento: Plataforma de E-commerce com Django

## 1. Introdução

Este documento detalha o plano de desenvolvimento para a criação de uma plataforma de e-commerce robusta, segura e escalável, utilizando o framework Django. O projeto tem como referência as funcionalidades do site `queopsnativa.com.br`, mas com uma implementação totalmente nova e moderna, seguindo os requisitos funcionais e não funcionais especificados.

## 2. Arquitetura da Aplicação

A arquitetura será baseada em um design modular, utilizando as "apps" do Django para separar as responsabilidades e garantir a manutenibilidade do código. A estrutura sugerida no documento de requisitos será adotada:

| App       | Responsabilidade                                                                      |
|-----------|---------------------------------------------------------------------------------------|
| `core`    | Lógica central, páginas estáticas (Home, Sobre, Contato) e configurações globais.     |
| `store`   | Gerenciamento de Produtos, Categorias, Busca e Filtros.                               |
| `cart`    | Funcionalidades do carrinho de compras, utilizando sessões do Django.                 |
| `orders`  | Lógica de checkout, criação e gerenciamento de pedidos, e integração com pagamentos. |
| `accounts`| Autenticação de usuários, perfis de cliente e histórico de pedidos.                   |

## 3. Tecnologias

| Componente      | Tecnologia                                                                                             |
|-----------------|--------------------------------------------------------------------------------------------------------|
| **Backend**     | Python 3.11+ com Django 5.x                                                                            |
| **Banco de Dados**| PostgreSQL para produção e SQLite para desenvolvimento.                                                |
| **Frontend**    | Utilizaremos o **Bootstrap 5** para um desenvolvimento ágil e um design responsivo e moderno.          |
| **Cache**       | **Redis** será implementado para otimizar o desempenho das consultas e o carregamento das páginas.     |
| **Pagamentos**  | Integração com a API do **Mercado Pago**, por sua robustez e popularidade no Brasil.                   |
| **Frete**       | Integração com a API dos **Correios** para cálculo de frete em tempo real.                             |
| **Testes**      | **Pytest** e **Pytest-Django** para a suíte de testes automatizados.                                     |
| **Containerização**| **Docker** e **Docker Compose** para padronizar os ambientes de desenvolvimento e produção.            |

## 4. Cronograma de Desenvolvimento (Estimativa)

O projeto será dividido em sprints semanais, com entregas incrementais das funcionalidades.

| Semana | Foco                                                                                                     |
|--------|----------------------------------------------------------------------------------------------------------|
| **1**  | Configuração do ambiente, estrutura do projeto, e desenvolvimento do app `core` e `accounts` (autenticação). |
| **2**  | Desenvolvimento do app `store` (CRUD de produtos e categorias no admin, listagem e detalhes de produtos).    |
| **3**  | Desenvolvimento do app `cart` (adição, remoção e atualização de itens no carrinho).                        |
| **4**  | Desenvolvimento do app `orders` (checkout, criação de pedidos) e integração com a API dos Correios.        |
| **5**  | Integração com o Mercado Pago e implementação dos e-mails transacionais.                                   |
| **6**  | Implementação dos testes automatizados, otimizações de desempenho e configuração do cache com Redis.       |
| **7**  | Finalização do frontend, ajustes de usabilidade e responsividade.                                          |
| **8**  | Preparação da documentação final (README.md), configuração do Docker e entrega do projeto.                 |

## 5. Próximos Passos

O próximo passo será a configuração do ambiente de desenvolvimento e a criação da estrutura inicial do projeto Django, conforme o planejamento da Semana 1. Após a sua aprovação deste plano, iniciarei a fase de codificação.

