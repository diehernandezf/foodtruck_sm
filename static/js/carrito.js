console.log('✅ carrito.js cargado');

window.deliverySeleccionado = 0;

// Obtener CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim(); //elimina espacios en blanco al inicio y final de cada string
            if (cookie.substring(0, name.length + 1) === (name + '=')) { // se comprueba si la cookie es la que buscamos
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1)); //extrae el valor despues del =
                break;
            }
        }
    }
    return cookieValue;
}

function mostrarNotificacion(mensaje, tipo) {
    console.log('mostrarNotificacion():', mensaje, tipo);

    const notif = document.createElement('div');
    notif.className = `fixed top-4 right-4 z-[100] px-6 py-3 rounded-lg shadow-lg text-white transform transition-transform duration-300 
    ${tipo === 'success' ? 'bg-green-500' : 'bg-red-500'}`;
    notif.textContent = mensaje;
    document.body.appendChild(notif);// se inserta el elemento en el body

    setTimeout(() => { //se configura la animacion de salida
        notif.style.transform = 'translateX(400px)'; // se translada hacia la derecha 400px
        setTimeout(() => notif.remove(), 300);//se elimina despues de tres segundos
    }, 3000);//espera tres segundos antes de ejecutar la funcion interna
}

// Actualizar contador de productos del icono del carrito del navbar
function actualizarContador(total_productos) {
    const carritoCount = document.getElementById('carrito-count');
    if (carritoCount) {
        carritoCount.textContent = total_productos;
        if (total_productos > 0) {
            carritoCount.classList.remove('hidden');
        } else {
            carritoCount.classList.add('hidden');
        }
    }
}

// Formatear precio
function formatearPrecio(precio) {
    return parseFloat(precio).toLocaleString('es-CL', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
}

// Abrir carrito
function abrirCarrito() {
    console.log('🛒 Abriendo carrito');
    const carritoPanel = document.getElementById('carrito-panel');
    const carritoOverlay = document.getElementById('carrito-overlay');

    if (carritoPanel && carritoOverlay) {
        carritoPanel.classList.remove('translate-x-full');
        carritoOverlay.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        cargarCarrito();
    }
}

function cargarCarrito() {
    console.log('Cargando contenido del carrito...');

    fetch('/carrito/ver/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos del carrito:', data);

            const carritoVacio = document.getElementById('carrito-vacio');
            const carritoContenido = document.getElementById('carrito-contenido');
            const carritoTotal = document.getElementById('carrito-total');

            if (data.total_items === 0) {
                carritoVacio.classList.remove('hidden');
                carritoContenido.classList.add('hidden');
            } else {
                carritoVacio.classList.add('hidden');
                carritoContenido.classList.remove('hidden');
                renderizarItems(data.items);
            }
            actualizarContador(data.total_items);

            if (window.actualizarTotal && typeof window.actualizarTotal === 'function') {
                window.actualizarTotal();
            }
        })
        .catch(error => {
            console.error('❌ Error al cargar carrito:', error);
            mostrarNotificacion('Error al cargar el carrito', 'error');
        });
}

// Renderizar items
function renderizarItems(items) {
    const carritoItems = document.getElementById('carrito-items');
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

function agregarAlCarrito(productoId, nombre, precio) {
    console.log('Se llama agregaAlCarrito()');
    console.log('Producto ID:', productoId);
    console.log('Nombre:', nombre);
    console.log('Precio:', precio); // sale precio 'indefinido'
    let cantidadProductos = 0;

    const csrftoken = getCookie('csrftoken');
    console.log('CSRF Token:', csrftoken ? 'Encontrado' : 'NO ENCONTRADO');
    if (!csrftoken) {
        console.error('CSRF token no encontrado');
        mostrarNotificacion('Error: Token de seguridad no encontrado', 'error');
        return;
    }

    if (!usuarioLogeado) {
        const modal = document.getElementById('modal');
        const content = modal.querySelector('.modal-content');
        modal.classList.remove('hidden');
        requestAnimationFrame(() => {
            content.classList.remove('scale-95', 'opacity-0');
            content.classList.add('scale-100', 'opacity-100');
        })
        return;
    }

    console.log('Enviando petición POST a /carrito/agregar/');

    fetch('/carrito/agregar/', {
        method: 'POST',
        headers: { // por ejemplo tipo de contenido o token
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ // el contenido que se va a enviar (generalmente en formato JSON)
            producto_id: productoId,
            cantidad: 1
        })
    })
        .then(response => {
            console.log('Respuesta recibida:', response.status, response.statusText);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => { // aca se ocupan los datos
            console.log('Data JSON:', data);
            if (data.success) {
                cantidadProductos = data.total_items
                actualizarContador(data.total_items);
                mostrarNotificacion(data.message || 'Producto agregado al carrito', 'success');
                abrirCarrito();
                if (typeof data.subtotal !== 'undefined') {
                    actualizarTotalCarrito(data.subtotal);
                }
                else {
                    mostrarNotificacion(data.message, 'error');
                }

            } else {
                console.error('Backend retornó success: false');
                mostrarNotificacion(data.message || 'Error al agregar producto', 'error');
            }
        })
        .catch(error => {
            console.error('Error en fetch:', error);
            mostrarNotificacion('Error de conexión: ' + error.message, 'error');
        });
}

function cerrarModal() {
    const modal = document.getElementById('modal');
    const content = modal.querySelector('.modal-content');
    content.classList.add('scale-95', 'opacity-0');
    content.classList.remove('scale-100', 'opacity-100');
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 200);
}

function formatCLP(valor) {
    return '$' + Number(valor).toLocaleString('es-CL', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    });
}

function actualizarTotalCarrito(subtotal) {
    const totalSpan = document.getElementById('carrito-total');
    if (!totalSpan) return;
    totalSpan.textContent = formatCLP(subtotal);
}

// Cambiar cantidad del propio producto en el carrito
function cambiarCantidad(itemId, nuevaCantidad) {
    console.log('Cambiar cantidadProducto():', itemId, nuevaCantidad);
    if (nuevaCantidad < 1) {
        eliminarItem(itemId);
        return;
    }

    fetch('/carrito/actualizar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
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
                if (typeof data.subtotal !== 'undefined') {
                    actualizarTotalCarrito(data.subtotal);
                }
                else {
                    mostrarNotificacion(data.message, 'error');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Error al actualizar cantidad', 'error');
        });
}

// Eliminar item
function eliminarItem(itemId) {
    console.log('EliminarItem():', itemId);

    fetch('/carrito/eliminar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            item_id: itemId
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarCarrito();
                if (typeof data.subtotal !== 'undefined') {
                    actualizarTotalCarrito(data.subtotal);
                }
                else {
                    mostrarNotificacion(data.message, 'error');
                }
                mostrarNotificacion(data.message, 'success');
            } else {
                mostrarNotificacion(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Error al eliminar producto', 'error');
        });
}

// Pagar  (transbank)
function pagar_carrito() {
    console.log('💳 Iniciando proceso de pago');

    // Obtener la dirección si existe
    const direccionInput = document.getElementById('direccion-input');
    let direccion = '';

    if (direccionInput) {
        // Verificar si el contenedor de dirección está visible
        const direccionContainer = document.getElementById('direccion-container');
        if (direccionContainer && !direccionContainer.classList.contains('hidden')) {
            direccion = direccionInput.value.trim();

            if (!direccion) {
                mostrarNotificacion('Por favor ingresa una dirección', 'error');
                return;
            }
        }
    }

    fetch('/pagos/iniciar_pago/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            direccion: direccion
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.url && data.token) {
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = data.url;

                    const tokenInput = document.createElement('input');
                    tokenInput.type = 'hidden';
                    tokenInput.name = 'token_ws';
                    tokenInput.value = data.token;

                    form.appendChild(tokenInput);
                    document.body.appendChild(form);
                    form.submit();
                } else {
                    mostrarNotificacion('Procesando pago...', 'success');
                }
            } else {
                mostrarNotificacion(data.message || 'Error al procesar el pago', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Error al iniciar el pago', 'error');
        });
}

// ============================================
// EVENT LISTENERS (después de que cargue el DOM)
// ============================================

document.addEventListener('DOMContentLoaded', function () {
    console.log('✅ DOM completamente cargado');

    const carritoBtn = document.getElementById('carrito-btn');
    const cerrarCarritoBtn = document.getElementById('cerrar-carrito');
    const carritoOverlay = document.getElementById('carrito-overlay');
    const vaciarCarritoBtn = document.getElementById('vaciar-carrito');
    const pagarBtn = document.getElementById('proceder-pago');

    // Cerrar carrito
    function cerrarCarrito() {
        const carritoPanel = document.getElementById('carrito-panel');
        carritoPanel.classList.add('translate-x-full');
        carritoOverlay.classList.add('hidden');
        document.body.style.overflow = '';
    }

    // Event listeners
    if (carritoBtn) {
        carritoBtn.addEventListener('click', abrirCarrito);
        console.log('✅ Event listener agregado a carrito-btn');
    }

    if (cerrarCarritoBtn) {
        cerrarCarritoBtn.addEventListener('click', cerrarCarrito);
        console.log('✅ Event listener agregado a cerrar-carrito');
    }

    if (carritoOverlay) {
        carritoOverlay.addEventListener('click', cerrarCarrito);
        console.log('✅ Event listener agregado a overlay');
    }

    if (pagarBtn) {
        pagarBtn.addEventListener('click', pagar_carrito);
        console.log('✅ Event listener agregado a proceder-pago');
    }

    // Vaciar carrito
    if (vaciarCarritoBtn) {
        vaciarCarritoBtn.addEventListener('click', function () {
            if (confirm('¿Estás seguro de vaciar el carrito?')) {
                fetch('/carrito/vaciar/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            cargarCarrito();
                            if (typeof data.subtotal !== 'undefined') {
                                actualizarTotalCarrito(data.subtotal);
                            }
                            else {
                                mostrarNotificacion(data.message, 'error');
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        mostrarNotificacion('Error al vaciar carrito', 'error');
                    });
            }
        });
        console.log('✅ Event listener agregado a vaciar-carrito');
    }

    // Cargar contador inicial
    console.log('🔄 Cargando contador inicial...');
    fetch('/carrito/ver/')
        .then(response => response.json())
        .then(data => {
            actualizarContador(data.total_items);
            console.log('✅ Contador inicial cargado:', data.total_items);
        })
        .catch(error => {
            console.error('❌ Error al cargar contador inicial:', error);
        });
});

// miPedido.html
document.addEventListener('DOMContentLoaded', function () {
    console.log('✅ miPedido script iniciado');

    try {
        const tipoGuardado = '{{ tipo_entrega }}';
        const direccionGuardada = '{{ direccion }}' || '';

        function formatCLP(valor) {
            return '$' + Number(valor).toLocaleString('es-CL', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0,
            });
        }

        function aplicarFormatoInicial(span) {
            if (!span) return;
            const texto = span.textContent.trim();
            if (!texto) return;

            // Deja solo dígitos, punto y signo menos (por si acaso)
            const numero = Number(texto.replace(/[^0-9.-]/g, ''));
            if (isNaN(numero)) return;

            span.textContent = formatCLP(numero);
        }

        // Referencias a los elementos que muestran montos
        const subtotalSpan = document.querySelector('[data-subtotal]');
        const deliverySpan = document.querySelector('[data-delivery]');
        const descuentoSpan = document.querySelector('[data-descuento]');
        const totalSpan = document.querySelector('[data-total]');

        aplicarFormatoInicial(subtotalSpan);
        aplicarFormatoInicial(descuentoSpan);
        aplicarFormatoInicial(deliverySpan);
        aplicarFormatoInicial(totalSpan);



        const btnRetiro = document.getElementById('btn-retiro');
        const btnDelivery = document.getElementById('btn-delivery');
        const direccionContainer = document.getElementById('direccion-container');
        const direccionInput = document.getElementById('direccion-input');

        if (tipoGuardado === 'delivery') {
            if (btnDelivery) btnDelivery.style.backgroundColor = '#fbbf24';
            if (btnRetiro) btnRetiro.style.backgroundColor = 'white';
            if (direccionContainer) direccionContainer.classList.remove('hidden');
            if (direccionInput && direccionGuardada) {
                direccionInput.value = direccionGuardada;
            }
        } else {
            if (btnRetiro) btnRetiro.style.backgroundColor = '#fbbf24';
            if (btnDelivery) btnDelivery.style.backgroundColor = 'white';
            if (direccionContainer) direccionContainer.classList.add('hidden');
        }

        function guardarTipoEntrega(tipo, direccion = '') {
            fetch('/ordenes/actualizar_tipo_entrega/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    tipo_entrega: tipo,
                    direccion: direccion
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('✅ Tipo de entrega y montos del backend', data);

                        // 🆕 Usamos SIEMPRE formatCLP para mostrar montos
                        if (subtotalSpan && data.subtotal !== undefined) {
                            subtotalSpan.textContent = formatCLP(data.subtotal);
                        }

                        if (descuentoSpan && data.descuento !== undefined) {
                            const desc = Number(data.descuento);
                            descuentoSpan.textContent = desc > 0
                                ? '-' + formatCLP(desc)
                                : '$0';
                        }

                        if (deliverySpan && data.delivery !== undefined) {
                            deliverySpan.textContent = formatCLP(data.delivery);
                        }

                        if (totalSpan && data.total !== undefined) {
                            totalSpan.textContent = formatCLP(data.total);
                        }
                    }
                })
                .catch(error => console.error('Error:', error));
        }

        if (btnRetiro) {
            btnRetiro.addEventListener('click', function () {
                console.log('CLICK RETIRO');
                btnRetiro.style.backgroundColor = '#fbbf24';
                if (btnDelivery) btnDelivery.style.backgroundColor = 'white';
                if (direccionContainer) direccionContainer.classList.add('hidden');
                guardarTipoEntrega('retiro', '');
            });
        }

        if (btnDelivery) {
            btnDelivery.addEventListener('click', function () {
                console.log('CLICK DELIVERY');
                btnDelivery.style.backgroundColor = '#fbbf24';
                if (btnRetiro) btnRetiro.style.backgroundColor = 'white';
                if (direccionContainer) direccionContainer.classList.remove('hidden');
                const direccion = direccionInput ? (direccionInput.value || '') : '';
                guardarTipoEntrega('delivery', direccion);
            });
        }

        // Guardar dirección cuando el usuario escriba
        if (direccionInput) {
            direccionInput.addEventListener('change', function () {
                guardarTipoEntrega('delivery', this.value);
            });
        }

    } catch (error) {
        console.error('❌ Error en miPedido script:', error);
    }
});
