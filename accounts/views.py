from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import (
    CreateView, UpdateView, DeleteView, ListView, 
    DetailView, TemplateView, View
)
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.utils import timezone
import json

from .models import Profile, Address, EmailVerificationToken
from .forms import (
    CustomUserCreationForm, ProfileForm, AddressForm,
    CustomPasswordChangeForm, PreferencesForm
)

User = get_user_model()


class CustomLoginView(LoginView):
    """Custom login view with enhanced functionality"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse('core:home')
    
    def form_valid(self, form):
        messages.success(self.request, f'Bem-vindo de volta, {form.get_user().get_full_name() or form.get_user().username}!')
        return super().form_valid(form)


class RegisterView(CreateView):
    """User registration view"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create user profile
        Profile.objects.get_or_create(user=self.object)
        
        # Auto login after registration
        username = form.cleaned_data.get('username') or form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)
            messages.success(
                self.request, 
                'Conta criada com sucesso! Bem-vindo à nossa loja!'
            )
            return redirect('core:home')
        
        messages.success(
            self.request,
            'Conta criada com sucesso! Faça login para continuar.'
        )
        return response
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'Erro ao criar conta. Verifique os dados e tente novamente.'
        )
        return super().form_invalid(form)


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view"""
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    
    def form_valid(self, form):
        messages.info(
            self.request,
            'Se existe uma conta com este e-mail, você receberá as instruções de recuperação em breve.'
        )
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view"""
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
    
    def form_valid(self, form):
        messages.success(
            self.request,
            'Senha alterada com sucesso! Você já pode fazer login com sua nova senha.'
        )
        return super().form_valid(form)


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Custom password change view for logged users"""
    template_name = 'accounts/password_change.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('accounts:password_change_done')
    
    def form_valid(self, form):
        messages.success(
            self.request,
            'Senha alterada com sucesso!'
        )
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Ensure profile exists
        profile, created = Profile.objects.get_or_create(user=user)
        
        context.update({
            'profile': profile,
            'addresses': user.addresses.all(),
            'recent_orders': user.orders.all()[:5] if hasattr(user, 'orders') else [],
        })
        return context


class UpdateProfileView(LoginRequiredMixin, View):
    """Update user profile information"""
    
    def post(self, request):
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)
        
        # Update user fields
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Update profile fields
        profile.phone = request.POST.get('phone', '')
        profile.birth_date = request.POST.get('birth_date') or None
        profile.cpf = request.POST.get('cpf', '')
        profile.gender = request.POST.get('gender', '')
        profile.save()
        
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('accounts:profile')


class UpdatePreferencesView(LoginRequiredMixin, View):
    """Update user preferences"""
    
    def post(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        # Update preferences
        profile.email_notifications = 'email_notifications' in request.POST
        profile.sms_notifications = 'sms_notifications' in request.POST
        profile.newsletter = 'newsletter' in request.POST
        profile.save()
        
        messages.success(request, 'Preferências atualizadas com sucesso!')
        return redirect('accounts:profile')


class AddressListView(LoginRequiredMixin, ListView):
    """List user addresses"""
    model = Address
    template_name = 'accounts/address_list.html'
    context_object_name = 'addresses'
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    """Create new address"""
    model = Address
    form_class = AddressForm
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:address_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Endereço adicionado com sucesso!')
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing address"""
    model = Address
    form_class = AddressForm
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:address_list')
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Endereço atualizado com sucesso!')
        return super().form_valid(form)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    """Delete address"""
    model = Address
    success_url = reverse_lazy('accounts:address_list')
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Endereço removido com sucesso!')
        return super().delete(request, *args, **kwargs)


class SetDefaultAddressView(LoginRequiredMixin, View):
    """Set address as default"""
    
    def post(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        
        # Remove default from other addresses
        Address.objects.filter(user=request.user).update(is_default=False)
        
        # Set this address as default
        address.is_default = True
        address.save()
        
        messages.success(request, 'Endereço padrão definido com sucesso!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return redirect('accounts:address_list')


class EmailVerificationView(LoginRequiredMixin, TemplateView):
    """Email verification page"""
    template_name = 'accounts/email_verification.html'
    
    def post(self, request):
        # Send verification email
        token = EmailVerificationToken.objects.create(user=request.user)
        
        verification_url = request.build_absolute_uri(
            reverse('accounts:confirm_email', kwargs={'token': token.token})
        )
        
        send_mail(
            'Confirme seu e-mail',
            f'Clique no link para confirmar seu e-mail: {verification_url}',
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False,
        )
        
        messages.info(request, 'E-mail de verificação enviado!')
        return redirect('accounts:profile')


class ConfirmEmailView(View):
    """Confirm email with token"""
    
    def get(self, request, token):
        try:
            verification_token = EmailVerificationToken.objects.get(
                token=token, 
                is_used=False
            )
            
            if verification_token.is_expired():
                messages.error(request, 'Token de verificação expirado.')
                return redirect('accounts:email_verification')
            
            # Mark email as verified
            profile, created = Profile.objects.get_or_create(
                user=verification_token.user
            )
            profile.email_verified = True
            profile.save()
            
            # Mark token as used
            verification_token.is_used = True
            verification_token.save()
            
            messages.success(request, 'E-mail verificado com sucesso!')
            
        except EmailVerificationToken.DoesNotExist:
            messages.error(request, 'Token de verificação inválido.')
        
        return redirect('accounts:profile')