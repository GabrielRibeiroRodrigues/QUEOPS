#!/bin/bash

# Script de entrada para o container Django

set -e

# Aguarda o banco de dados estar disponível
echo "Aguardando o banco de dados..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Banco de dados disponível!"

# Executa migrações
echo "Executando migrações..."
python manage.py migrate --noinput

# Coleta arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Cria superusuário se não existir
echo "Verificando superusuário..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='Sistema'
    )
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
"

# Inicia o servidor
echo "Iniciando servidor Django..."
exec python manage.py runserver 0.0.0.0:8000
