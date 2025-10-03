from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import Profile, Address, EmailVerificationToken, LoginHistory

User = get_user_model()


class ProfileInline(admin.StackedInline):
    """
    Inline para o Profile no admin do User
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'
    extra = 0


class AddressInline(admin.TabularInline):
    """
    Inline para endereços no admin do User
    """
    model = Address
    extra = 0
    verbose_name_plural = 'Endereços'


class CustomUserAdmin(BaseUserAdmin):
    """
    Admin customizado para User
    """
    inlines = (ProfileInline, AddressInline)
    list_display = (
        'username', 'email', 'first_name', 'last_name', 
        'is_staff', 'date_joined', 'get_profile_phone'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    def get_profile_phone(self, obj):
        """Exibe o telefone do perfil"""
        try:
            return obj.profile.phone
        except Profile.DoesNotExist:
            return '-'
    get_profile_phone.short_description = 'Telefone'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin para Profile
    """
    list_display = (
        'user', 'phone', 'birth_date', 'gender', 
        'email_verified', 'newsletter', 'created_at'
    )
    list_filter = (
        'gender', 'email_verified', 'newsletter', 
        'email_notifications', 'sms_notifications', 'created_at'
    )
    search_fields = ('user__username', 'user__email', 'phone', 'cpf')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Informações Pessoais', {
            'fields': ('phone', 'birth_date', 'cpf', 'gender')
        }),
        ('Preferências', {
            'fields': (
                'email_notifications', 'sms_notifications', 
                'newsletter', 'email_verified'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    Admin para Address
    """
    list_display = (
        'user', 'name', 'type', 'city', 'state', 
        'is_default', 'created_at'
    )
    list_filter = ('type', 'is_default', 'state', 'created_at')
    search_fields = (
        'user__username', 'user__email', 'name', 
        'street', 'city', 'neighborhood'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Usuário e Tipo', {
            'fields': ('user', 'type', 'name', 'is_default')
        }),
        ('Endereço', {
            'fields': (
                'street', 'number', 'complement', 
                'neighborhood', 'city', 'state', 'zip_code'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """
    Admin para EmailVerificationToken
    """
    list_display = (
        'user', 'token', 'created_at', 'is_used', 'is_expired_status'
    )
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email', 'token')
    readonly_fields = ('token', 'created_at', 'is_expired_status')
    
    def is_expired_status(self, obj):
        """Mostra se o token está expirado"""
        return obj.is_expired()
    is_expired_status.boolean = True
    is_expired_status.short_description = 'Expirado'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """
    Admin para LoginHistory
    """
    list_display = (
        'user', 'login_time', 'ip_address', 
        'is_successful', 'get_short_user_agent'
    )
    list_filter = ('is_successful', 'login_time')
    search_fields = ('user__username', 'user__email', 'ip_address')
    readonly_fields = ('login_time',)
    date_hierarchy = 'login_time'
    
    def get_short_user_agent(self, obj):
        """Exibe uma versão encurtada do user agent"""
        if obj.user_agent:
            return obj.user_agent[:50] + '...' if len(obj.user_agent) > 50 else obj.user_agent
        return '-'
    get_short_user_agent.short_description = 'User Agent'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        """Desabilita a adição manual de histórico de login"""
        return False


# Register UserAdmin
admin.site.register(User, CustomUserAdmin)