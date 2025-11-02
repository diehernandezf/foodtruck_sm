from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(label='Ingresa correo electronico')
    password = forms.CharField(widget=forms.PasswordInput, label='Ingresa contraseña')