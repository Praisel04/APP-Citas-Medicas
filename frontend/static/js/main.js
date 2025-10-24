const user_id = localStorage.getItem("user_id");
const rol = localStorage.getItem("rol");
const API_URL = `http://localhost:8000/citas?user_id=${user_id}&rol=${rol}`;
const statusDiv = document.getElementById("status");
const table = document.getElementById("tabla-citas");
const tbody = document.getElementById("citas-body");
const formDiv = document.getElementById("formulario-cita");
const btnNuevaCita = document.getElementById("btn-nueva-cita");
const formCita = document.getElementById("form-nueva-cita");
const nombreUsuarioSpan = document.getElementById("nombre-usuario");

// Verificar si el usuario está logueado
if (!user_id) {
  mostrarMensaje("❌ Debes iniciar sesión para ver tus citas.");
  window.location.href = "./login.html";
}

// Mostrar nombre de usuario
nombreUsuarioSpan.textContent = localStorage.getItem("nombre");

// Mostrar formulario
btnNuevaCita.addEventListener("click", () => {
  formDiv.classList.toggle("d-none");
});

// ============================
// 📅 CARGAR CITAS DEL USUARIO
// ============================
async function cargarCitas() {
  tbody.innerHTML = "";
  statusDiv.textContent = "Cargando citas...";
  table.classList.add("d-none");

  try {
    const resp = await fetch(API_URL);
    if (!resp.ok) throw new Error("Error HTTP " + resp.status);
    const citas = await resp.json();

    if (citas.length === 0) {
      statusDiv.textContent = "No hay citas registradas.";
      return;
    }

    statusDiv.classList.add("d-none");
    table.classList.remove("d-none");

    citas.forEach(cita => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${cita.nombre_paciente || "—"}</td>
        <td>${cita.nombre_cita}</td>
        <td>${new Date(cita.fecha_hora).toLocaleString()}</td>
        <td class="estado ${cita.estado}">${cita.estado}</td>
        <td>
          <button class="btn btn-sm btn-warning me-2" onclick="abrirModalEditar('${cita.id}', '${cita.nombre_cita}', '${cita.fecha_hora}', '${cita.estado}')">✏️ Editar</button>
          <button class="btn btn-sm btn-danger" onclick="eliminarCita('${cita.id}')">🗑️ Eliminar</button>
        </td>
      `;
      tbody.appendChild(row);
    });
  } catch (err) {
    console.error(err);
    statusDiv.textContent = "❌ Error cargando citas. Revisa el backend.";
  }
}

// ============================
// 🧾 CREAR NUEVA CITA
// ============================
formCita.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fecha_hora = document.getElementById("fecha_hora").value;
  const nombre_cita = document.getElementById("nombre_cita").value;
  if (!fecha_hora) return mostrarMensaje("Debes seleccionar una fecha y hora.");

  try {
    const resp = await fetch("http://localhost:8000/citas", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id, nombre_cita, fecha_hora, estado: "programada" })
    });

    const data = await resp.json();
    if (resp.ok) {
      mostrarMensaje("✅ Cita creada correctamente");
      formDiv.classList.add("d-none");
      formCita.reset();
      cargarCitas();
    } else {
      mostrarMensaje("❌ " + (data.error || "Error al crear la cita"));
    }
  } catch (err) {
    console.error(err);
    mostrarMensaje("❌ Error de conexión con el servidor");
  }
});

// ============================
// ❌ ELIMINAR CITA
// ============================
async function eliminarCita(id) {
  if (!confirm("¿Seguro que deseas eliminar esta cita?")) return;

  try {
    const resp = await fetch(`http://localhost:8000/citas/${id}?user_id=${user_id}`, {
      method: "DELETE"
    });
    const data = await resp.json();

    if (resp.ok) {
      mostrarMensaje("🗑️ Cita eliminada correctamente");
      cargarCitas();
    } else {
      mostrarMensaje("❌ " + (data.error || "No se pudo eliminar la cita"));
    }
  } catch (err) {
    console.error(err);
    mostrarMensaje("❌ Error eliminando la cita");
  }
}

// ============================
// ✏️ EDITAR CITA
// ============================

// Crear dinámicamente un modal Bootstrap y añadirlo al DOM

let citaEditando = null;
let modalEditar = null;

function abrirModalEditar(id, nombre, fecha, estado) {
  citaEditando = id;
  document.getElementById("edit-id").value = id;
  document.getElementById("edit-nombre-cita").value = nombre;
  document.getElementById("edit-fecha-hora").value = fecha.slice(0, 16);
  document.getElementById("edit-estado").value = estado;

  modalEditar = new bootstrap.Modal(document.getElementById("modal-editar"));
  modalEditar.show();
}

// 🔹 Vinculamos el listener directamente al botón después de insertarlo
document.getElementById("btnGuardarEdicion").addEventListener("click", async () => {
  const nombre_cita = document.getElementById("edit-nombre-cita").value;
  const fecha_hora = document.getElementById("edit-fecha-hora").value;
  const estado = document.getElementById("edit-estado").value;

  

  try {
    const resp = await fetch(`http://localhost:8000/citas/${citaEditando}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id, nombre_cita, fecha_hora, estado })
    });

    const data = await resp.json();
    console.log("🔵 Respuesta del servidor:", data);

    if (resp.ok) {
      mostrarMensaje("✅ Cita actualizada correctamente");
      modalEditar.hide();
      cargarCitas();
    } else {
      mostrarMensaje("❌ " + (data.error || "Error al editar la cita"));
    }
  } catch (err) {
    console.error("❌ Error de conexión:", err);
    mostrarMensaje("❌ No se pudo conectar al servidor");
  }
});

// ==========================
// 🧾 Función de mensajes UX
// ==========================
const mensajeAviso = document.getElementById("mensaje-aviso");

/**
 * Muestra un mensaje en pantalla.
 * @param {string} texto - El mensaje a mostrar.
 * @param {"success"|"error"|"info"} tipo - Tipo de mensaje (controla el color).
 */
function mostrarMensaje(texto, tipo = "info") {
  mensajeAviso.textContent = texto;
  mensajeAviso.classList.remove("d-none", "alert-success", "alert-danger", "alert-info");

  if (tipo === "success") mensajeAviso.classList.add("alert-success");
  else if (tipo === "error") mensajeAviso.classList.add("alert-danger");
  else mensajeAviso.classList.add("alert-info");

  // Desaparece automáticamente después de unos segundos (opcional)
  setTimeout(() => {
    mensajeAviso.classList.add("d-none");
  }, 4000);
}



// ============================
// 🚪 CERRAR SESIÓN
// ============================
document.getElementById("btn-salir").addEventListener("click", () => {
  localStorage.clear();
  window.location.href = "./login.html";
});

// Llamar a la función cuando se carga la página
document.addEventListener("DOMContentLoaded", () => {
  cargarCitas();
});
