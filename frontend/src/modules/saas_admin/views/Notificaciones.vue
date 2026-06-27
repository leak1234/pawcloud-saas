<template>
  <div class="container-fluid mt-4">
    <h2 class="mb-4 text-dark fw-bold">📢 Avisos del Sistema</h2>
    
    <div class="row g-4">
      <div class="col-md-5">
        <FormularioAviso 
          :aviso-editando="avisoSeleccionado" 
          @actualizar-lista="cargarAvisos" 
          @cancelar-edicion="avisoSeleccionado = null" 
        />
      </div>

      <div class="col-md-7">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-header bg-white fw-bold text-dark border-bottom d-flex justify-content-between align-items-center">
            <span>Historial de Publicaciones</span>
            <button class="btn btn-sm btn-outline-secondary fw-bold" @click="cargarAvisos">🔄 Actualizar</button>
          </div>
          
          <div class="card-body overflow-auto" style="max-height: 600px;">
            <div v-if="avisos.length === 0" class="text-center text-muted py-5">
              <i class="bi bi-megaphone fs-1 d-block mb-2"></i>
              No hay avisos publicados en el sistema.
            </div>

            <div v-for="aviso in avisos" :key="aviso.id" 
                 class="card mb-3 border-start border-4 shadow-sm"
                 :class="{
                   'border-info': aviso.tipo === 'info',
                   'border-warning': aviso.tipo === 'warning',
                   'border-danger': aviso.tipo === 'danger',
                   'opacity-50 bg-light': !aviso.activo
                 }">
              <div class="card-body py-3">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h5 class="card-title mb-0 fw-bold text-dark" :class="{'text-decoration-line-through': !aviso.activo}">
                    {{ aviso.titulo }}
                  </h5>
                  <span class="badge bg-white text-secondary border border-secondary-subtle shadow-sm" style="font-size: 0.7rem;">
                    📅 {{ aviso.fecha_creacion }}
                  </span>
                </div>
                <p class="card-text text-secondary mb-3 small" style="white-space: pre-wrap;">{{ aviso.mensaje }}</p>
                
                <div class="d-flex justify-content-between border-top pt-2 mt-2">
                  <div>
                    <button class="btn btn-sm btn-outline-primary me-2 fw-bold shadow-sm" @click="prepararEdicion(aviso)" title="Editar">✏️ Editar</button>
                    <button class="btn btn-sm btn-outline-danger fw-bold shadow-sm" @click="borrarAviso(aviso.id)" title="Eliminar">🗑️ Borrar</button>
                  </div>
                  <button class="btn btn-sm fw-bold shadow-sm" 
                          :class="aviso.activo ? 'btn-outline-secondary' : 'btn-outline-success'"
                          @click="cambiarEstado(aviso.id)">
                    {{ aviso.activo ? '👁️ Ocultar a Clínicas' : '✅ Volver a Publicar' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Swal from 'sweetalert2';
import FormularioAviso from '../components/avisos/FormularioAviso.vue'; // <-- IMPORTACIÓN DEL HIJO

const avisos = ref([]);
const avisoSeleccionado = ref(null); // Estado centralizado que se envía al hijo

const cargarAvisos = async () => {
  try {
    const respuesta = await fetch('http://localhost:5000/api/admin/avisos');
    avisos.value = await respuesta.json();
  } catch (error) { console.error(error); }
};

const prepararEdicion = (aviso) => {
  avisoSeleccionado.value = aviso; // Le pasa el objeto al hijo y el hijo se encarga del resto
};

const cambiarEstado = async (id) => {
  try {
    await fetch(`http://localhost:5000/api/admin/avisos/${id}/estado`, { method: 'PUT' });
    cargarAvisos();
  } catch (error) { console.error(error); }
};

const borrarAviso = async (id) => {
  const resultado = await Swal.fire({
    title: '¿Eliminar aviso?',
    text: "Esta acción lo borrará permanentemente de todas las clínicas.",
    icon: 'warning',
    showCancelButton: true,
    buttonsStyling: false,
    customClass: {
      confirmButton: 'btn btn-danger px-4 mx-2 shadow-sm fw-bold', 
      cancelButton: 'btn btn-secondary px-4 mx-2 shadow-sm fw-bold',
      popup: 'rounded-4 shadow-lg border-0' 
    },
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar',
    reverseButtons: true
  });

  if (resultado.isConfirmed) {
    try {
      const respuesta = await fetch(`http://localhost:5000/api/admin/avisos/${id}`, { method: 'DELETE' });
      if (respuesta.ok) {
        Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Aviso eliminado correctamente', showConfirmButton: false, timer: 2000 });
        cargarAvisos();
      }
    } catch (error) { 
      Swal.fire({ title: 'Error', text: 'Hubo un problema al intentar eliminar el aviso.', icon: 'error' });
    }
  }
};

onMounted(() => {
  cargarAvisos();
});
</script>