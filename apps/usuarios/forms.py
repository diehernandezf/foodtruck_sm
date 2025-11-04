from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(label='Ingresa nombre de usuario')
    password = forms.CharField(widget=forms.PasswordInput, label='Ingresa contraseña')