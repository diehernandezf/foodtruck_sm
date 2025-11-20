document.addEventListener("DOMContentLoaded", () => {
    const botones = document.querySelectorAll(".btn-completado");
    console.log("🔍 Botones .btn-completado encontrados:", botones.length);

    botones.forEach(btn => {
        btn.addEventListener("click", () => {
            console.log("🖱️ Click en botón LISTO, data-url:", btn.dataset.url);

            const url = btn.dataset.url;   // 👈 ahora SÍ existe url

            fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json",
                },
            })
            .then(res => res.json())
            .then(data => {
                console.log("📦 Respuesta del servidor:", data);
                if (data.success) {
                    btn.parentElement.querySelector(".estado-texto").innerText = "completado";
                    btn.style.display = "none";
                }
            })
            .catch(err => console.error("❌ Error en fetch:", err));
            window.location.reload();
        });
    });
});

// Funcion para obtener csrf
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}