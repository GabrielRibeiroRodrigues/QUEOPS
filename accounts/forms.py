from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

from .models import Profile, Address

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    Formulário customizado para criação de usuários
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sobrenome'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu melhor e-mail'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Telefone (WhatsApp)'
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Criar senha'
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar senha'
        })
    )
    
    accept_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    newsletter = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este e-mail já está em uso.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove todos os caracteres não numéricos
            phone_digits = re.sub(r'\D', '', phone)
            if len(phone_digits) < 10 or len(phone_digits) > 11:
                raise ValidationError('Telefone deve ter 10 ou 11 dígitos.')
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Use email as username
        
        if commit:
            user.save()
            
            # Create profile
            profile = Profile.objects.create(
                user=user,
                phone=self.cleaned_data.get('phone', ''),
                newsletter=self.cleaned_data.get('newsletter', True)
            )
        
        return user


class ProfileForm(forms.ModelForm):
    """
    Formulário para edição do perfil do usuário
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sobrenome'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'E-mail'
        })
    )
    
    class Meta:
        model = Profile
        fields = ('phone', 'birth_date', 'cpf', 'gender')
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remove caracteres não numéricos
            cpf_digits = re.sub(r'\D', '', cpf)
            if len(cpf_digits) != 11:
                raise ValidationError('CPF deve ter 11 dígitos.')
            
            # Validação básica de CPF
            if cpf_digits == cpf_digits[0] * 11:
                raise ValidationError('CPF inválido.')
        
        return cpf


class AddressForm(forms.ModelForm):
    """
    Formulário para endereços do usuário
    """
    class Meta:
        model = Address
        fields = (
            'type', 'name', 'street', 'number', 'complement', 
            'neighborhood', 'city', 'state', 'zip_code', 'is_default'
        )
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Casa, Trabalho, Casa dos Pais'
            }),
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da rua'
            }),
            'number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número'
            }),
            'complement': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apto, bloco, etc. (opcional)'
            }),
            'neighborhood': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bairro'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estado (UF)',
                'maxlength': '2'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('zip_code')
        if zip_code:
            # Remove caracteres não numéricos
            zip_digits = re.sub(r'\D', '', zip_code)
            if len(zip_digits) != 8:
                raise ValidationError('CEP deve ter 8 dígitos.')
        return zip_code
    
    def clean_state(self):
        state = self.cleaned_data.get('state')
        if state:
            state = state.upper()
            valid_states = [
                'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 
                'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 
                'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
            ]
            if state not in valid_states:
                raise ValidationError('Estado inválido.')
        return state


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Formulário customizado para alteração de senha
    """
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha atual'
        })
    )
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nova senha'
        })
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nova senha'
        })
    )


class PreferencesForm(forms.ModelForm):
    """
    Formulário para preferências do usuário
    """
    class Meta:
        model = Profile
        fields = ('email_notifications', 'sms_notifications', 'newsletter')
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'sms_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'newsletter': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class ContactForm(forms.Form):
    """
    Formulário de contato
    """
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu e-mail'
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Assunto'
        })
    )
    
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Sua mensagem',
            'rows': 5
        })
    )
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 2:
            raise ValidationError('Nome deve ter pelo menos 2 caracteres.')
        return name
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise ValidationError('Mensagem deve ter pelo menos 10 caracteres.')
        return message