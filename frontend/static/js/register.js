document.getElementById('formRegister').addEventListener('submit', async (event) => {
    event.preventDefault();

    const nombre = document.getElementById('nombre_usuario').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('contrasenia').value.trim();
    const rol = document.getElementById('rol').value.trim();

    const mensaje = document.getElementById('mensaje_aviso');
    mensaje.classList.add('d-none');

    try {
        const response = await fetch('http://localhost:8000/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre, email, password, rol })
        });

        const result = await response.json();

        if (response.ok) {
            // ✅ Guardamos los datos para usarlos luego
            localStorage.setItem("user_id", result.user_id);
            localStorage.setItem("nombre", nombre);
            localStorage.setItem("rol", rol);

            // ✅ Mensaje visual de confirmación
            mensaje.textContent = result.message;
            mensaje.className = 'alert alert-success';
            mensaje.classList.remove('d-none');

            // // ✅ Opcional: redirigir automáticamente tras unos segundos
            // setTimeout(() => {
            //     window.location.href = "./login.html";
            // }, 2000);

            // Limpieza del formulario
            document.getElementById('formRegister').reset();
            console.log('Usuario registrado:', result);
            console.log('Rol asignado:', rol);
        } else {
            mensaje.textContent = result.error || 'Error en el registro';
            mensaje.className = 'alert alert-danger';
            mensaje.classList.remove('d-none');
        }
    } catch (error) {
        mensaje.textContent = 'Error de conexión con el servidor';
        mensaje.className = 'alert alert-danger';
        mensaje.classList.remove('d-none');
        console.error('Error:', error);
    }
});
