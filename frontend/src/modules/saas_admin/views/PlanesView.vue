<template>
  <div class="container-fluid mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="text-dark fw-bold fs-3">Planes de Suscripción</h1>
      <button class="btn btn-primary fw-bold shadow-sm" @click="abrirModalCrear">
        + Nuevo Plan
      </button>
    </div>

    <div class="row g-4">
      <div class="col-md-4 col-lg-3" v-for="plan in planes" :key="plan.id">
        <div class="card h-100 shadow-sm border-0 text-center position-relative" :class="{'opacity-50': !plan.activo}">
          <div v-if="!plan.activo" class="position-absolute top-0 end-0 bg-danger text-white px-2 py-1 small rounded-bottom-start shadow-sm fw-bold">
            Suspendido
          </div>

          <div class="card-body d-flex flex-column pt-4">
            <h4 class="fw-bold text-uppercase text-secondary mt-2">{{ plan.nombre }}</h4>
            <div class="my-3">
              <span class="fs-4 text-secondary">$</span>
              <span class="display-4 fw-bold text-dark">{{ plan.precio }}</span>
            </div>
            
            <ul class="list-unstyled mt-3 mb-4 text-start mx-auto" style="max-width: 200px;">
              <li class="mb-2"><strong>{{ plan.limite_usuarios }}</strong> Usuarios permitidos</li>
              <li class="mb-2"><strong>{{ plan.limite_pacientes }}</strong> Pacientes (Mascotas)</li>
              <li class="mb-2 text-success fw-semibold">✔️ Soporte técnico 24/7</li>
            </ul>

            <div class="mt-auto d-flex justify-content-center gap-2 border-top pt-3">
              <button class="btn btn-sm btn-outline-warning text-dark fw-bold shadow-sm" @click="abrirModalEditar(plan)">
                ✏️ Editar
              </button>
              <button class="btn btn-sm fw-bold shadow-sm" :class="plan.activo ? 'btn-outline-danger' : 'btn-outline-success'" @click="alternarEstado(plan)">
                {{ plan.activo ? '🛑 Suspender' : '✅ Reactivar' }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="planes.length === 0" class="col-12">
        <div class="card border-0 shadow-sm text-center py-5 bg-light rounded-4">
          <h4 class="text-muted fw-bold">No hay planes registrados</h4>
          <p class="text-secondary">Crea tu primer plan de suscripción para que las clínicas puedan registrarse.</p>
        </div>
      </div>
    </div>

    <ModalPlan 
      :show="modal.show" 
      :editandoId="modal.editandoId" 
      :planData="modal.data"
      @close="modal.show = false" 
      @guardado="alGuardar" 
    />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import Swal from 'sweetalert2';
import ModalPlan from '../components/planes/ModalPlan.vue'; // <-- IMPORTACIÓN DEL HIJO

const planes = ref([]);

// ESTADO DEL MODAL
const modal = ref({ show: false, editandoId: null, data: null });

const cargarPlanes = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/admin/planes');
    planes.value = res.data;
  } catch (error) {
    console.error("Error al cargar planes:", error);
  }
};

const abrirModalCrear = () => {
  modal.value = { show: true, editandoId: null, data: null };
};

const abrirModalEditar = (plan) => {
  modal.value = { show: true, editandoId: plan.id, data: plan };
};

const alGuardar = () => {
  modal.value.show = false;
  cargarPlanes();
};

// --- ALTERNAR ESTADO CON CONFIRMACIÓN ---
const alternarEstado = async (plan) => {
  const accionText = plan.activo ? 'Suspender' : 'Activar';
  const descripcionText = plan.activo 
    ? 'Las nuevas clínicas no podrán contratar este plan.' 
    : 'El plan volverá a estar disponible para todos.';
  
  const botonClase = plan.activo ? 'btn-danger' : 'btn-success';

  const resultado = await Swal.fire({
    title: `¿${accionText} el plan ${plan.nombre}?`,
    text: descripcionText,
    icon: 'warning',
    showCancelButton: true,
    buttonsStyling: false,
    customClass: {
      confirmButton: `btn ${botonClase} px-4 mx-2 shadow-sm fw-bold`,
      cancelButton: 'btn btn-secondary px-4 mx-2 shadow-sm fw-bold',
      popup: 'rounded-4 shadow-lg border-0'
    },
    confirmButtonText: `Sí, ${accionText}`,
    cancelButtonText: 'Cancelar',
    reverseButtons: true
  });

  if (resultado.isConfirmed) {
    try {
      const res = await axios.post(`http://localhost:5000/api/admin/planes/${plan.id}/cambiar-estado`);
      plan.activo = res.data.nuevo_estado;
      
      Swal.fire({
        toast: true, position: 'top-end', icon: 'success',
        title: `Plan ${plan.activo ? 'activado' : 'suspendido'}`,
        showConfirmButton: false, timer: 2000
      });
    } catch (error) {
      Swal.fire({ title: 'Error', text: 'No se pudo cambiar el estado del plan.', icon: 'error', buttonsStyling: false, customClass: { confirmButton: 'btn btn-primary px-4' } });
    }
  }
};

onMounted(() => {
  cargarPlanes();
});
</script>

<style scoped>
/* Transición suave para cuando un plan se suspende */
.card {
  transition: opacity 0.3s ease, transform 0.2s ease;
}
.card:hover {
  transform: translateY(-5px);
}
.opacity-50 {
  opacity: 0.7 !important;
  background-color: #f8f9fa;
  filter: grayscale(0.5);
}
</style>