from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User
import re


class UserRegistrationForm(UserCreationForm):
    """
    Formulário para cadastro de novos usuários.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu sobrenome'
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(11) 99999-9999'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar classes CSS aos campos
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nome de usuário'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Senha'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme a senha'
        })
        
        # Personalizar help texts
        self.fields['username'].help_text = 'Obrigatório. 150 caracteres ou menos. Apenas letras, números e @/./+/-/_.'
        self.fields['password1'].help_text = 'Sua senha deve conter pelo menos 8 caracteres.'
        self.fields['password2'].help_text = 'Digite a mesma senha novamente para verificação.'
    
    def clean_email(self):
        """
        Validar se o email já não está em uso.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este email já está em uso.')
        return email
    
    def clean_phone_number(self):
        """
        Validar formato do telefone.
        """
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Remove caracteres não numéricos
            phone_digits = re.sub(r'\D', '', phone)
            if len(phone_digits) < 10 or len(phone_digits) > 11:
                raise ValidationError('Número de telefone inválido.')
        return phone
    
    def save(self, commit=True):
        """
        Salvar o usuário com os dados adicionais.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """
    Formulário para edição do perfil do usuário.
    """
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'birth_date', 'cpf', 'address_line_1', 'address_line_2',
            'city', 'state', 'postal_code'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua, número'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Complemento (opcional)'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SP'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
        }
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'phone_number': 'Telefone',
            'birth_date': 'Data de Nascimento',
            'cpf': 'CPF',
            'address_line_1': 'Endereço',
            'address_line_2': 'Complemento',
            'city': 'Cidade',
            'state': 'Estado',
            'postal_code': 'CEP',
        }
    
    def clean_email(self):
        """
        Validar se o email já não está em uso por outro usuário.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este email já está em uso por outro usuário.')
        return email
    
    def clean_cpf(self):
        """
        Validar formato do CPF.
        """
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remove caracteres não numéricos
            cpf_digits = re.sub(r'\D', '', cpf)
            if len(cpf_digits) != 11:
                raise ValidationError('CPF deve conter 11 dígitos.')
            
            # Validação básica de CPF (algoritmo simplificado)
            if cpf_digits == cpf_digits[0] * 11:
                raise ValidationError('CPF inválido.')
        
        return cpf
    
    def clean_postal_code(self):
        """
        Validar formato do CEP.
        """
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code:
            # Remove caracteres não numéricos
            cep_digits = re.sub(r'\D', '', postal_code)
            if len(cep_digits) != 8:
                raise ValidationError('CEP deve conter 8 dígitos.')
        
        return postal_code
