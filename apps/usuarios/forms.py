from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UsuarioPersonalizado
from django.contrib.auth import get_user_model

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


User = get_user_model()


class RegistroForm(UserCreationForm):
    telefono = forms.CharField(label="Teléfono", required=True, max_length=15)

    class Meta:
        model = User
        # orden de los campos en el formulario
        fields = ['username', 'email', 'telefono', 'password1', 'password2']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Email',
            'telefono': 'Teléfono',
            'password1': 'Contraseña',
            'password2': 'Contraseña (confirmación)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # quitar textos largos de ayuda de las contraseñas
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

        # estilos generales para todos los campos
        for nombre, campo in self.fields.items():
            campo.widget.attrs.update({
                'class': (
                    'w-full px-3 py-2 rounded-lg border text-sm bg-gray-50 '
                    'border-gray-300 text-gray-900 placeholder-gray-400 '
                    'focus:outline-none focus:ring-2 focus:ring-yellow-400 '
                    'focus:border-yellow-500 transition'
                ),
                'placeholder': campo.label
            })

        # configuración específica del teléfono (solo los números después del +56)
        self.fields['telefono'].widget.attrs.update({
            'placeholder': '9 1234 5678',
            'maxlength': '9',
            'inputmode': 'tel',
            'pattern': '9[0-9]{8}',
        })
