from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.RegisterView.as_view(), name='register'),
    
    # Password reset URLs
    path('recuperar-senha/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('recuperar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('redefinir-senha/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('redefinir-senha/completo/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Profile URLs
    path('perfil/', views.ProfileView.as_view(), name='profile'),
    path('perfil/atualizar/', views.UpdateProfileView.as_view(), name='update_profile'),
    path('perfil/preferencias/', views.UpdatePreferencesView.as_view(), name='update_preferences'),
    
    # Address URLs
    path('enderecos/', views.AddressListView.as_view(), name='address_list'),
    path('enderecos/adicionar/', views.AddressCreateView.as_view(), name='address_create'),
    path('enderecos/<int:pk>/editar/', views.AddressUpdateView.as_view(), name='address_update'),
    path('enderecos/<int:pk>/excluir/', views.AddressDeleteView.as_view(), name='address_delete'),
    path('enderecos/<int:pk>/padrao/', views.SetDefaultAddressView.as_view(), name='set_default_address'),
    
    # Account management
    path('alterar-senha/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('alterar-senha/sucesso/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
    
    # Email verification (if needed)
    path('verificar-email/', views.EmailVerificationView.as_view(), name='email_verification'),
    path('confirmar-email/<str:token>/', views.ConfirmEmailView.as_view(), name='confirm_email'),
]