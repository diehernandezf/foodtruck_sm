// Carrito de compras - JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const carritoBtn = document.getElementById('carrito-btn');
    const carritoPanel = document.getElementById('carrito-panel');
    const cerrarCarritoBtn = document.getElementById('cerrar-carrito');
    const carritoOverlay = document.getElementById('carrito-overlay');
    const carritoCount = document.getElementById('carrito-count');
    const carritoItems = document.getElementById('carrito-items');
    const carritoTotal = document.getElementById('carrito-total');
    const carritoVacio = document.getElementById('carrito-vacio');
    const carritoContenido = document.getElementById('carrito-contenido');
    const vaciarCarritoBtn = document.getElementById('vaciar-carrito');

    // Obtener CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Abrir carrito
    function abrirCarrito() {
        carritoPanel.classList.remove('translate-x-full');
        carritoOverlay.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        cargarCarrito();
    }

    // Cerrar carrito
    function cerrarCarrito() {
        carritoPanel.classList.add('translate-x-full');
        carritoOverlay.classList.add('hidden');
        document.body.style.overflow = '';
    }

    // Event listeners
    carritoBtn.addEventListener('click', abrirCarrito);
    cerrarCarritoBtn.addEventListener('click', cerrarCarrito);
    carritoOverlay.addEventListener('click', cerrarCarrito);

    // Agregar al carrito
    window.agregarAlCarrito = function(productoId, nombre) {
        fetch('/carrito/agregar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                producto_id: productoId,
                cantidad: 1
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                actualizarContador(data.total_items);
                mostrarNotificacion(data.message, 'success');
                abrirCarrito();
            } else {
                mostrarNotificacion(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Error al agregar al carrito', 'error');
        });
    };

    // Cargar contenido del carrito
    function cargarCarrito() {
        fetch('/carrito/ver/')
            .then(response => response.json())
            .then(data => {
                if (data.total_items === 0) {
                    carritoVacio.classList.remove('hidden');
                    carritoContenido.classList.add('hidden');
                } else {
                    carritoVacio.classList.add('hidden');
                    carritoContenido.classList.remove('hidden');
                    renderizarItems(data.items);
                    carritoTotal.textContent = `$${formatearPrecio(data.total)}`;
                }
                actualizarContador(data.total_items);
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarNotificacion('Error al cargar el carrito', 'error');
            });
    }

    // Renderizar items del carrito
    function renderizarItems(items) {
        carritoItems.innerHTML = '';
        items.forEach(item => {
            const itemHtml = `
                <div class="flex gap-4 p-4 bg-surface-light dark:bg-surface-dark rounded-lg" data-item-id="${item.id}">
                    <img src="${item.imagen_url}" alt="${item.nombre}" 
                         class="w-20 h-20 object-cover rounded-lg">
                    <div class="flex-1">
                        <h4 class="font-semibold text-sm">${item.nombre}</h4>
                        <p class="text-sm text-text-secondary-light dark:text-text-secondary-dark">
                            $${formatearPrecio(item.precio_unitario)}
                        </p>
                        <div class="flex items-center gap-2 mt-2">
                            <button onclick="cambiarCantidad(${item.id}, ${item.cantidad - 1})" 
                                    class="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 flex items-center justify-center">
                                <span class="text-lg">-</span>
                            </button>
                            <span class="w-8 text-center font-semibold">${item.cantidad}</span>
                            <button onclick="cambiarCantidad(${item.id}, ${item.cantidad + 1})" 
                                    class="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 flex items-center justify-center">
                                <span class="text-lg">+</span>
                            </button>
                            <button onclick="eliminarItem(${item.id})" 
                                    class="ml-auto text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300">
                                <span class="material-symbols-outlined">delete</span>
                            </button>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="font-bold">$${formatearPrecio(item.total)}</p>
                    </div>
                </div>
            `;
            carritoItems.innerHTML += itemHtml;
        });
    }

    // Cambiar cantidad
    window.cambiarCantidad = function(itemId, nuevaCantidad) {
        if (nuevaCantidad < 1) {
            eliminarItem(itemId);
            return;
        }

        fetch('/carrito/actualizar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                item_id: itemId,
                cantidad: nuevaCantidad
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarCarrito();
            } else {
                mostrarNotificacion(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Error al actualizar cantidad', 'error');
        });
    };

    // Eliminar item
    window.eliminarItem = function(itemId) {
        fetch('/carrito/eliminar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                item_id: itemId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarCarrito();
                mostrarNotificacion(data.message, 'success');
            } else {
                mostrarNotificacion(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Error al eliminar producto', 'error');
        });
    };

    // Vaciar carrito
    vaciarCarritoBtn.addEventListener('click', function() {
        if (confirm('¿Estás seguro de vaciar el carrito?')) {
            fetch('/carrito/vaciar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    cargarCarrito();
                    mostrarNotificacion(data.message, 'success');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarNotificacion('Error al vaciar carrito', 'error');
            });
        }
    });

    // Actualizar contador del carrito
    function actualizarContador(total) {
        carritoCount.textContent = total;
        if (total > 0) {
            carritoCount.classList.remove('hidden');
        } else {
            carritoCount.classList.add('hidden');
        }
    }

    // Formatear precio
    function formatearPrecio(precio) {
        return parseFloat(precio).toLocaleString('es-CL', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        });
    }

    // Mostrar notificación
    function mostrarNotificacion(mensaje, tipo) {
        const notif = document.createElement('div');
        notif.className = `fixed top-4 right-4 z-[100] px-6 py-3 rounded-lg shadow-lg text-white transform transition-transform duration-300 ${
            tipo === 'success' ? 'bg-green-500' : 'bg-red-500'
        }`;
        notif.textContent = mensaje;
        document.body.appendChild(notif);

        setTimeout(() => {
            notif.style.transform = 'translateX(400px)';
            setTimeout(() => notif.remove(), 300);
        }, 3000);
    }

    // Cargar contador al iniciar
    fetch('/carrito/ver/')
        .then(response => response.json())
        .then(data => {
            actualizarContador(data.total_items);
        })
        .catch(error => console.error('Error:', error));
});