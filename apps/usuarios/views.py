from django.shortcuts import render

# Create your views here.

def ir_crud_usuarios(request):
    return render(request, 'crud_usuarios.html')

def ir_registro(request):
    return render(request, 'registro.html')

def ir_login(request):
    return render(request, 'login.html')