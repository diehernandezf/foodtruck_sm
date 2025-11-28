from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .forms import LoginForm, RegistroForm

from django.contrib.auth import get_user_model # se obtiene el modelo de usuario activo del proyecto
User = get_user_model()
# Create your views here.

#def ir_crud_usuarios(request):
#    return render(request, 'crud_usuarios.html')
User = get_user_model()
def ir_registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # 👇 OPCIONAL: si quieres que el username sea igual al email
            if not user.username:
                user.username = user.email

            user.save()

            # Iniciar sesión automáticamente después de registrarse
            login(request, user)
            return redirect('productos:home')
        else:
            # Si el formulario no es válido, se vuelve a mostrar con errores
            return render(request, 'registro.html', {'form': form})
    else:
        form = RegistroForm()
        return render(request, 'registro.html', {'form': form})

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
                return HttpResponse('Usuario no encontrado')
            except User.MultipleObjectsReturned:
                return HttpResponse('Multiples usuarios con el mismo correo')
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