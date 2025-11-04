from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .forms import LoginForm

from django.contrib.auth.models import User
# Create your views here.

#def ir_crud_usuarios(request):
#    return render(request, 'crud_usuarios.html')

def ir_registro(request):
    return render(request, 'registro.html')

def ir_login(request):
    if request.method == 'POST': # Metodo de solicitud http POST, sirve para enviar informacion al servidor
        form = LoginForm(request.POST) # Guardamos en form las variables enviadas en LoginForm()
        if form.is_valid():
            cd = form.cleaned_data # Limpiamos los datos
            email = cd['email']
            password = cd['password']
            try: # Try para controlar si no hay usuario o si hay mas de un usuario con mismo email
                user_obj = User.objects.get(email=email) # Obtenemos el usuario de email = al que se ingreso en el formulario
                username = user_obj.username # Se guarda en username el username del usuario obtenido
            except User.DoesNotExist:
                HttpResponse('Usuario no encontrado')
            except User.MultipleObjectsReturned:
                HttpResponse('Multiples usuarios con el mismo correo')
            user = authenticate(request,
                                username = username,
                                password = password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('productos:home')
                else:
                    return HttpResponse('El usuario no esta activo')
            else:
                return HttpResponse('La informacion no es correcta')
    else:
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    
def ir_logout(request):
    logout(request)
    return render(request, 'logged_out.html')
    
@login_required
def dashboard(request):
    return render(request, 'crud_usuarios.html')