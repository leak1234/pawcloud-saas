<template>
  <div class="container-fluid mt-4">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 gap-3">
      <h1 class="text-dark fw-bold fs-3 mb-0">👥 Gestión de Personal</h1>
      <button class="btn btn-primary fw-bold shadow-sm px-4" @click="abrirCrear">+ Nuevo Empleado</button>
    </div>

    <div class="card shadow-sm border-0 mb-3 bg-white rounded-3">
      <div class="card-body py-3">
        <div class="row g-2 align-items-center">
          <div class="col-md-5">
            <div class="input-group">
              <span class="input-group-text bg-light border-secondary-subtle">🔍</span>
              <input type="text" class="form-control bg-light border-secondary-subtle" placeholder="Buscar por nombre o correo..." v-model="filtroTexto">
            </div>
          </div>
          <div class="col-md-3">
            <select class="form-select bg-light border-secondary-subtle" v-model="filtroRol">
              <option value="">Todos los roles</option>
              <option value="admin">Admin</option>
              <option value="veterinario">Veterinario</option>
              <option value="recepcionista">Recepcionista</option>
              <option value="cajero">Cajero</option>
              <option value="peluquero">Peluquero</option>
            </select>
          </div>
          <div class="col-md-4 d-flex justify-content-md-end align-items-center">
            <div class="form-check form-switch mb-0">
              <input class="form-check-input" type="checkbox" role="switch" id="switchInactivos" v-model="viendoInactivos" @change="cargarEmpleados">
              <label class="form-check-label fw-bold text-secondary ms-2" for="switchInactivos" style="cursor: pointer;">
                {{ viendoInactivos ? '🔴 Viendo Suspendidos' : '🟢 Viendo Activos' }}
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0 rounded-3 bg-white">
      <div class="card-body p-0 table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-dark">
            <tr>
              <th class="ps-4 py-3">Nombre del Personal</th>
              <th class="py-3">Correo Electrónico</th>
              <th class="py-3">Rol del Sistema</th>
              <th class="text-center py-3">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="empleadosPaginados.length === 0">
              <td colspan="4" class="text-center py-5 text-muted">No se encontraron empleados con estos filtros.</td>
            </tr>
            <tr v-for="emp in empleadosPaginados" :key="emp.id" :class="{'bg-light opacity-75': viendoInactivos}">
              <td class="ps-4 fw-bold" :class="viendoInactivos ? 'text-secondary text-decoration-line-through' : 'text-dark'">
                {{ emp.nombre_completo }}
              </td>
              <td class="text-secondary">{{ emp.email }}</td>
              <td>
                <span class="badge bg-primary bg-opacity-10 text-primary border border-primary px-2" v-if="emp.rol === 'veterinario'">🩺 Veterinario</span>
                <span class="badge bg-success bg-opacity-10 text-success border border-success px-2" v-else-if="emp.rol === 'recepcionista'">📅 Recepcionista</span>
                <span class="badge bg-warning bg-opacity-10 text-warning border border-warning px-2" v-else-if="emp.rol === 'cajero'">💰 Cajero</span>
                <span class="badge bg-info bg-opacity-10 text-info border border-info px-2" v-else-if="emp.rol === 'peluquero'">✂️ Peluquero</span>
                <span class="badge bg-dark px-2" v-else-if="emp.rol === 'admin'">⚙️ Admin Principal</span>
              </td>
              <td class="text-center">
                <template v-if="!viendoInactivos">
                  <template v-if="emp.rol !== 'admin'">
                    <button class="btn btn-warning btn-sm text-dark fw-bold shadow-sm mx-1" @click="abrirEditar(emp)">✏️ Editar</button>
                    <button class="btn btn-danger btn-sm text-white fw-bold shadow-sm mx-1" @click="eliminarEmpleado(emp)">Suspender</button>
                  </template>
                  <template v-else>
                    <span class="text-muted small fw-bold"><i class="bi bi-lock-fill"></i> Protegido</span>
                  </template>
                </template>
                <template v-else>
                  <button class="btn btn-success btn-sm fw-bold shadow-sm" @click="restaurarEmpleado(emp)">♻️ Restaurar</button>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="card-footer bg-white border-top d-flex justify-content-between align-items-center py-3" v-if="totalPaginas > 0">
        <span class="text-muted small fw-bold">Mostrando página {{ paginaActual }} de {{ totalPaginas }}</span>
        <div class="btn-group shadow-sm">
          <button class="btn btn-sm btn-outline-secondary" :disabled="paginaActual === 1" @click="paginaActual--">Anterior</button>
          <button class="btn btn-sm btn-outline-secondary" :disabled="paginaActual === totalPaginas" @click="paginaActual++">Siguiente</button>
        </div>
      </div>
    </div>

    <ModalEmpleado 
      :show="modal.show" 
      :modo-edicion="modal.edit" 
      :empleado-data="modal.data" 
      @close="modal.show = false" 
      @guardado="alGuardar" 
    />

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import Swal from 'sweetalert2';
import ModalEmpleado from '../components/empleados/ModalEmpleado.vue'; // <--- IMPORTACIÓN DEL HIJO

const empleados = ref([]);
const clinicaId = sessionStorage.getItem('clinica_id');
const viendoInactivos = ref(false);

const filtroTexto = ref('');
const filtroRol = ref('');
const paginaActual = ref(1);
const elementosPorPagina = 8;

// ESTADO DEL MODAL
const modal = ref({ show: false, edit: false, data: null });

watch([filtroTexto, filtroRol, viendoInactivos], () => { paginaActual.value = 1; });

const empleadosFiltrados = computed(() => {
  return empleados.value.filter(emp => {
    const coincideTexto = emp.nombre_completo.toLowerCase().includes(filtroTexto.value.toLowerCase()) || emp.email.toLowerCase().includes(filtroTexto.value.toLowerCase());
    const coincideRol = filtroRol.value === '' || emp.rol === filtroRol.value;
    return coincideTexto && coincideRol;
  });
});

const totalPaginas = computed(() => Math.ceil(empleadosFiltrados.value.length / elementosPorPagina) || 1);
const empleadosPaginados = computed(() => empleadosFiltrados.value.slice((paginaActual.value - 1) * elementosPorPagina, paginaActual.value * elementosPorPagina));

const cargarEmpleados = async () => {
  const estado = viendoInactivos.value ? 'inactivos' : 'activos';
  const respuesta = await fetch(`http://localhost:5000/api/clinica/${clinicaId}/empleados?estado=${estado}`);
  if (respuesta.ok) empleados.value = await respuesta.json();
};

// CONTROLES DEL MODAL
const abrirCrear = () => modal.value = { show: true, edit: false, data: null };
const abrirEditar = (emp) => modal.value = { show: true, edit: true, data: emp };
const alGuardar = () => { modal.value.show = false; cargarEmpleados(); };

// ACCIONES DE SEGURIDAD
const eliminarEmpleado = async (emp) => {
  const resultado = await Swal.fire({
    title: '¿Suspender empleado?',
    html: `<b>${emp.nombre_completo}</b> ya no podrá iniciar sesión en la clínica.`,
    icon: 'warning', showCancelButton: true, confirmButtonColor: '#dc3545', confirmButtonText: 'Sí, suspender', reverseButtons: true
  });
  if (resultado.isConfirmed) {
    const respuesta = await fetch(`http://localhost:5000/api/clinica/${clinicaId}/empleados/${emp.id}`, { method: 'DELETE' });
    if (respuesta.ok) { cargarEmpleados(); Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Acceso suspendido', showConfirmButton: false, timer: 2000 }); }
  }
};

const restaurarEmpleado = async (emp) => {
  const resultado = await Swal.fire({
    title: '¿Restaurar acceso?',
    html: `<b>${emp.nombre_completo}</b> volverá a operar en el sistema.`,
    icon: 'question', showCancelButton: true, confirmButtonColor: '#198754', confirmButtonText: 'Restaurar', reverseButtons: true
  });
  if (resultado.isConfirmed) {
    const respuesta = await fetch(`http://localhost:5000/api/clinica/${clinicaId}/empleados/${emp.id}/restaurar`, { method: 'PATCH' });
    if (respuesta.ok) { cargarEmpleados(); Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Acceso restaurado', showConfirmButton: false, timer: 2000 }); }
  }
};

onMounted(() => { if (clinicaId) cargarEmpleados(); });
</script>