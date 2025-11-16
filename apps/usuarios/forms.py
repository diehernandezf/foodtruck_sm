from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UsuarioPersonalizado

class LoginForm(forms.Form):
    email = forms.EmailField(label='Ingresa nombre de usuario')
    password = forms.CharField(widget=forms.PasswordInput, label='Ingresa contraseña')

class UsuarioCreationForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", required=False)
    last_name = forms.CharField(label="Apellidos", required=False)
    email = forms.EmailField(label="Correo", required=True)
    telefono = forms.CharField(label="Teléfono", required=False)

    class Meta(UserCreationForm.Meta):
        model = UsuarioPersonalizado
        fields = ("username", "first_name", "last_name", "email", "telefono")

class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = UsuarioPersonalizado
        fields = ("username", "first_name", "last_name", "email", "telefono", "is_active", "is_staff")
