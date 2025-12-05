from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse

from .forms import LoginForm, RegistroForm

from django.contrib.auth import get_user_model # se obtiene el modelo de usuario activo del proyecto
# Create your views here.

User = get_user_model()
def ir_registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if not user.username:
                user.username = user.email
            user.save()

            login(request, user)
            return redirect('productos:home')
        else:
            return render(request, 'registro.html', {'form': form})
    else:
        form = RegistroForm()
        return render(request, 'registro.html', {'form': form})

def ir_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST) 
        if form.is_valid():
            cd = form.cleaned_data 
            email = cd['email']
            password = cd['password']
            try: 
                user_obj = User.objects.get(email=email) 
                username = user_obj.username 
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