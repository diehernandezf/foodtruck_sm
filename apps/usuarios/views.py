from django.shortcuts import render

from django.contrib.auth import authenticate, login
from django.http import HttpResponse

from .forms import LoginForm
# Create your views here.

def ir_crud_usuarios(request):
    return render(request, 'crud_usuarios.html')

def ir_registro(request):
    return render(request, 'registro.html')

def ir_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                email = cd['email'],
                                password = cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Usuario autenticado')
                else:
                    return HttpResponse('El usuario no esta activo')
            else:
                HttpResponse('La informacion no es correcta')
    else:
        form = LoginForm()
        return render(request, 'login.html', {form: form})