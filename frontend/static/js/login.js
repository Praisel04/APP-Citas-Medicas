document.getElementById('formLogin').addEventListener('submit', async (event) => {
        event.preventDefault(); // Evita recargar la página

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value.trim();
        const mensaje = document.getElementById('mensaje_aviso');
        mensaje.classList.add('d-none');

        try {
            const response = await fetch('http://localhost:8000/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const result = await response.json();

            if (response.ok) {
                mensaje.textContent = result.message;
                mensaje.className = 'alert alert-success';
                mensaje.classList.remove('d-none');

                // Guardar user_id y nombre en localStorage
                localStorage.setItem('user_id', result.user_id);
                localStorage.setItem('nombre', result.nombre);
                localStorage.setItem('rol', result.rol);

                console.log('Usuario logueado:', result);
                console.log('Rol del usuario:', result.rol); 
                

                // Redirigir a la página principal de citas después de 2 segundos
                setTimeout(() => {
                    window.location.href = './index.html';
                }, 1500);

            } else {
                mensaje.textContent = result.error || 'Error en el inicio de sesión';
                mensaje.className = 'alert alert-danger';
                mensaje.classList.remove('d-none');
            }

        } catch (error) {
            console.error('Error:', error);
            mensaje.textContent = 'Error de conexión con el servidor';
            mensaje.className = 'alert alert-danger';
            mensaje.classList.remove('d-none');
        }
    });