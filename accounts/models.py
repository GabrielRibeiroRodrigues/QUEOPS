from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


class User(AbstractUser):
    """
    Modelo de usuário customizado que estende o AbstractUser do Django.
    Adiciona campos específicos para o e-commerce.
    """
    email = models.EmailField(
        'E-mail',
        unique=True,
        help_text='Endereço de e-mail único para login e comunicação.'
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Número de telefone deve estar no formato: '+999999999'. Até 15 dígitos permitidos."
    )
    phone_number = models.CharField(
        'Telefone',
        validators=[phone_regex],
        max_length=17,
        blank=True,
        help_text='Número de telefone para contato.'
    )
    
    birth_date = models.DateField(
        'Data de Nascimento',
        null=True,
        blank=True,
        help_text='Data de nascimento do usuário.'
    )
    
    cpf = models.CharField(
        'CPF',
        max_length=14,
        blank=True,
        unique=True,
        null=True,
        help_text='CPF do usuário (formato: 000.000.000-00).'
    )
    
    # Campos de endereço
    address_line_1 = models.CharField(
        'Endereço',
        max_length=255,
        blank=True,
        help_text='Rua, número e complemento.'
    )
    
    address_line_2 = models.CharField(
        'Complemento',
        max_length=255,
        blank=True,
        help_text='Apartamento, bloco, etc.'
    )
    
    city = models.CharField(
        'Cidade',
        max_length=100,
        blank=True,
        help_text='Cidade de residência.'
    )
    
    state = models.CharField(
        'Estado',
        max_length=2,
        blank=True,
        help_text='Estado (UF) de residência.'
    )
    
    postal_code = models.CharField(
        'CEP',
        max_length=9,
        blank=True,
        help_text='CEP no formato 00000-000.'
    )
    
    # Campos de controle
    is_verified = models.BooleanField(
        'E-mail Verificado',
        default=False,
        help_text='Indica se o e-mail do usuário foi verificado.'
    )
    
    created_at = models.DateTimeField(
        'Data de Criação',
        auto_now_add=True,
        help_text='Data e hora de criação da conta.'
    )
    
    updated_at = models.DateTimeField(
        'Última Atualização',
        auto_now=True,
        help_text='Data e hora da última atualização dos dados.'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_address(self):
        """Retorna o endereço completo formatado."""
        address_parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.state,
            self.postal_code
        ]
        return ', '.join([part for part in address_parts if part])

    def has_complete_profile(self):
        """Verifica se o perfil do usuário está completo."""
        required_fields = [
            self.first_name,
            self.last_name,
            self.phone_number,
            self.address_line_1,
            self.city,
            self.state,
            self.postal_code
        ]
        return all(field for field in required_fields)


class Profile(models.Model):
    """
    Modelo de perfil do usuário que estende as informações do User padrão do Django.
    """
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]
    
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuário'
    )
    
    phone = models.CharField(
        'Telefone',
        max_length=20,
        blank=True,
        help_text='Número de telefone para contato'
    )
    
    birth_date = models.DateField(
        'Data de Nascimento',
        null=True,
        blank=True
    )
    
    cpf = models.CharField(
        'CPF',
        max_length=14,
        blank=True,
        unique=True,
        null=True
    )
    
    gender = models.CharField(
        'Gênero',
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True
    )
    
    # Preferences
    email_notifications = models.BooleanField(
        'Notificações por E-mail',
        default=True
    )
    
    sms_notifications = models.BooleanField(
        'Notificações por SMS',
        default=False
    )
    
    newsletter = models.BooleanField(
        'Newsletter',
        default=True
    )
    
    email_verified = models.BooleanField(
        'E-mail Verificado',
        default=False
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name() or self.user.username}"


class Address(models.Model):
    """
    Modelo para endereços do usuário.
    """
    ADDRESS_TYPES = [
        ('home', 'Casa'),
        ('work', 'Trabalho'),
        ('other', 'Outro'),
    ]
    
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name='Usuário'
    )
    
    type = models.CharField(
        'Tipo',
        max_length=10,
        choices=ADDRESS_TYPES,
        default='home'
    )
    
    name = models.CharField(
        'Nome do Endereço',
        max_length=100,
        help_text='Ex: Casa, Trabalho, Casa dos Pais'
    )
    
    street = models.CharField(
        'Rua',
        max_length=200
    )
    
    number = models.CharField(
        'Número',
        max_length=10
    )
    
    complement = models.CharField(
        'Complemento',
        max_length=100,
        blank=True
    )
    
    neighborhood = models.CharField(
        'Bairro',
        max_length=100
    )
    
    city = models.CharField(
        'Cidade',
        max_length=100
    )
    
    state = models.CharField(
        'Estado',
        max_length=2
    )
    
    zip_code = models.CharField(
        'CEP',
        max_length=9
    )
    
    is_default = models.BooleanField(
        'Endereço Padrão',
        default=False
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.street}, {self.number}"
    
    def save(self, *args, **kwargs):
        # Se este endereço está sendo marcado como padrão,
        # remover o padrão dos outros endereços do usuário
        if self.is_default:
            Address.objects.filter(
                user=self.user, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    def get_full_address(self):
        """Retorna o endereço completo formatado."""
        parts = [
            f"{self.street}, {self.number}",
        ]
        
        if self.complement:
            parts.append(self.complement)
        
        parts.extend([
            self.neighborhood,
            f"{self.city}/{self.state}",
            f"CEP: {self.zip_code}"
        ])
        
        return " - ".join(parts)


class EmailVerificationToken(models.Model):
    """
    Tokens para verificação de e-mail.
    """
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='email_tokens'
    )
    
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Token de Verificação de E-mail'
        verbose_name_plural = 'Tokens de Verificação de E-mail'
    
    def __str__(self):
        return f"Token para {self.user.email}"
    
    def is_expired(self):
        """Verifica se o token expirou (24 horas)."""
        expiry_time = self.created_at + timezone.timedelta(hours=24)
        return timezone.now() > expiry_time


class LoginHistory(models.Model):
    """
    Histórico de logins do usuário.
    """
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='login_history'
    )
    
    login_time = models.DateTimeField(auto_now_add=True)
    
    ip_address = models.GenericIPAddressField(
        'Endereço IP',
        null=True,
        blank=True
    )
    
    user_agent = models.TextField(
        'User Agent',
        blank=True
    )
    
    is_successful = models.BooleanField(
        'Login Bem-sucedido',
        default=True
    )
    
    class Meta:
        verbose_name = 'Histórico de Login'
        verbose_name_plural = 'Históricos de Login'
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"