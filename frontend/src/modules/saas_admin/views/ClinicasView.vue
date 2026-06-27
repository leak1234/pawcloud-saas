<template>
  <div class="container-fluid mt-4">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 gap-3">
      <h1 class="text-dark fw-bold fs-3 mb-0">Gestión de Clínicas</h1>
      <button class="btn btn-primary fw-bold shadow-sm" @click="abrirModalCrear">
        + Nueva Clínica
      </button>
    </div>

    <div class="card shadow-sm border-0 mb-3 bg-light">
      <div class="card-body py-3">
        <div class="row g-2">
          <div class="col-md-8">
            <input type="text" class="form-control border-secondary-subtle"
              placeholder="🔍 Buscar por negocio, administrador o correo..." v-model="filtroTexto" />
          </div>
          <div class="col-md-4">
            <select class="form-select border-secondary-subtle fw-semibold text-truncate" v-model="filtroEstado">
              <option value="activos">🟢 Solo Clínicas Activas</option>
              <option value="inactivos">🔴 Solo Clínicas Suspendidas</option>
              <option value="vencidas">🟡 Solo Clínicas Vencidas</option>
              <option value="todos">⚪ Mostrar Todas</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-body p-0 table-responsive">
        <table class="table table-hover table-striped mb-0 align-middle">
          <thead class="table-dark">
            <tr>
              <th class="ps-3 d-none d-md-table-cell">ID</th>
              <th>Negocio</th>
              <th class="d-none d-lg-table-cell">NIT</th>
              <th class="d-none d-lg-table-cell">Dirección Física</th>
              <th class="d-none d-md-table-cell">Plan</th>
              <th>Vencimiento</th>
              <th class="d-none d-md-table-cell">Administrador</th>
              <th class="d-none d-lg-table-cell">Correo Electrónico</th>
              <th>Estado</th>
              <th class="text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="clinica in clinicasPaginadas" :key="clinica.id">
              <td class="ps-3 d-none d-md-table-cell">{{ clinica.id }}</td>

              <td class="fw-bold text-dark">
                {{ clinica.nombre_negocio }}
                <div class="d-block d-md-none mt-1">
                  <span class="badge bg-primary bg-opacity-10 text-primary border border-primary-subtle"
                    style="font-size: 0.7rem;">
                    {{ clinica.nombre_plan }}
                  </span>
                </div>
              </td>

              <td class="d-none d-lg-table-cell">{{ clinica.nit }}</td>
              <td class="d-none d-lg-table-cell">{{ clinica.direccion }}</td>

              <td class="d-none d-md-table-cell">
                <span class="badge bg-primary bg-opacity-10 text-primary border border-primary-subtle">
                  {{ clinica.nombre_plan }}
                </span>
              </td>

              <td class="fw-semibold text-secondary">
                🗓️ <span class="d-none d-sm-inline">{{ clinica.fecha_vencimiento }}</span>
                <span class="d-inline d-sm-none">{{ clinica.fecha_vencimiento.slice(5) }}</span>
              </td>

              <td class="d-none d-md-table-cell">{{ clinica.nombre_usuario }}</td>
              <td class="d-none d-lg-table-cell">{{ clinica.email }}</td>

              <td>
                <span class="badge shadow-sm text-uppercase" :class="{
                  'bg-success': clinica.estado_real === 'activa',
                  'bg-warning text-dark': clinica.estado_real === 'vencida',
                  'bg-danger': clinica.estado_real === 'suspendida'
                }">
                  {{ clinica.estado_real === 'activa' ? 'Activa' :
                    clinica.estado_real === 'vencida' ? 'Vencida' : 'Suspendida' }}
                </span>
              </td>

              <td class="text-center">
                <div class="d-flex flex-column flex-lg-row justify-content-center align-items-center gap-2">
                  <button class="btn btn-info btn-sm text-white fw-bold shadow-sm w-100"
                    @click="renovarSuscripcion(clinica)">
                    🔄 <span class="d-none d-lg-inline">Renovar</span>
                  </button>
                  <button class="btn btn-warning btn-sm text-dark fw-bold shadow-sm w-100"
                    @click="abrirModalEditar(clinica)">
                    ✏️ <span class="d-none d-lg-inline">Editar</span>
                  </button>
                  <button class="btn btn-sm fw-bold text-white shadow-sm w-100"
                    :class="clinica.activo ? 'btn-danger' : 'btn-success'" @click="alternarEstado(clinica)">
                    {{ clinica.activo ? 'Suspender' : 'Reactivar' }}
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="clinicasPaginadas.length === 0">
              <td colspan="10" class="text-center text-muted py-4">
                No se encontraron clínicas que coincidan con los filtros.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card-footer bg-white d-flex flex-column flex-md-row justify-content-between align-items-center py-3 border-0 border-top" v-if="totalPaginas > 1">
        <span class="text-muted small mb-2 mb-md-0 fw-semibold">
          Mostrando {{ (paginaActual - 1) * elementosPorPagina + 1 }} a 
          {{ Math.min(paginaActual * elementosPorPagina, clinicasFiltradas.length) }} 
          de {{ clinicasFiltradas.length }} clínicas
        </span>
        
        <div class="btn-group shadow-sm">
          <button class="btn btn-outline-primary btn-sm fw-bold" 
                  :disabled="paginaActual === 1" 
                  @click="paginaActual--">
            ◀ Anterior
          </button>
          <button class="btn btn-primary btn-sm fw-bold px-3" disabled>
            Página {{ paginaActual }} de {{ totalPaginas }}
          </button>
          <button class="btn btn-outline-primary btn-sm fw-bold" 
                  :disabled="paginaActual === totalPaginas" 
                  @click="paginaActual++">
            Siguiente ▶
          </button>
        </div>
      </div>
    </div>

    <ModalClinica 
      :show="modal.show" 
      :editandoId="modal.editandoId" 
      :clinicaData="modal.data"
      :planesDisponibles="planesDisponibles"
      @close="modal.show = false" 
      @guardado="alGuardar" 
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import axios from 'axios';
import Swal from 'sweetalert2';
import ModalClinica from '../components/clinicas/ModalClinica.vue'; // <-- IMPORTACIÓN DEL HIJO

const listaClinicas = ref([]);
const planesDisponibles = ref([]);
const filtroTexto = ref('');
const filtroEstado = ref('activos');
const paginaActual = ref(1);
const elementosPorPagina = ref(6);
let intervaloActualizacion;

// ESTADO DEL MODAL
const modal = ref({ show: false, editandoId: null, data: null });

watch([filtroTexto, filtroEstado], () => {
  paginaActual.value = 1;
});

const clinicasFiltradas = computed(() => {
  return listaClinicas.value.filter(clinica => {
    let pasaEstado = true;
    if (filtroEstado.value === 'activos') {
      pasaEstado = clinica.estado_real !== 'suspendida';
    } else if (filtroEstado.value === 'inactivos') {
      pasaEstado = clinica.estado_real === 'suspendida';
    } else if (filtroEstado.value === 'vencidas') {
      pasaEstado = clinica.estado_real === 'vencida';
    }

    const termino = filtroTexto.value.toLowerCase();
    const pasaTexto =
      clinica.nombre_negocio.toLowerCase().includes(termino) ||
      clinica.nombre_usuario.toLowerCase().includes(termino) ||
      clinica.email.toLowerCase().includes(termino);

    return pasaEstado && pasaTexto;
  });
});

const totalPaginas = computed(() => Math.ceil(clinicasFiltradas.value.length / elementosPorPagina.value));
const clinicasPaginadas = computed(() => {
  const inicio = (paginaActual.value - 1) * elementosPorPagina.value;
  return clinicasFiltradas.value.slice(inicio, inicio + elementosPorPagina.value);
});

const cargarClinicas = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/admin/clinicas');
    listaClinicas.value = res.data;
  } catch (error) { console.error(error); }
};

const cargarPlanes = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/admin/planes');
    // Filtramos para que el select solo muestre planes activos
    planesDisponibles.value = res.data.filter(p => p.activo);
  } catch (error) { console.error(error); }
};

// CONTROLES DEL MODAL
const abrirModalCrear = () => {
  modal.value = { show: true, editandoId: null, data: null };
};

const abrirModalEditar = (clinica) => {
  modal.value = { show: true, editandoId: clinica.id, data: clinica };
};

const alGuardar = () => {
  modal.value.show = false;
  cargarClinicas();
};

// --- ALERTA CONFIRMAR AL SUSPENDER CLÍNICA ---
const alternarEstado = async (clinica) => {
  const accionText = clinica.activo ? 'suspender' : 'reactivar';
  const descripcionText = clinica.activo 
    ? 'El administrador y sus empleados ya no podrán ingresar al sistema.' 
    : 'La clínica volverá a tener acceso a sus datos.';
  const botonClase = clinica.activo ? 'btn-danger' : 'btn-success';

  const resultado = await Swal.fire({
    title: `¿Deseas ${accionText} esta clínica?`,
    text: descripcionText,
    icon: 'warning',
    showCancelButton: true,
    buttonsStyling: false,
    customClass: {
      confirmButton: `btn ${botonClase} px-4 mx-2 shadow-sm`,
      cancelButton: 'btn btn-secondary px-4 mx-2 shadow-sm',
      popup: 'rounded-4 shadow-lg border-0'
    },
    confirmButtonText: `Sí, ${accionText}`,
    cancelButtonText: 'Cancelar'
  });

  if (resultado.isConfirmed) {
    try {
      await axios.post(`http://localhost:5000/api/admin/clinicas/${clinica.id}/cambiar-estado`);
      cargarClinicas();
      Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: `Clínica ${clinica.activo ? 'suspendida' : 'reactivada'}`, showConfirmButton: false, timer: 2000 });
    } catch (error) {
      Swal.fire({ title: 'Error', text: 'No se pudo cambiar el estado.', icon: 'error' });
    }
  }
};

// --- ALERTA CONFIRMAR RENOVACIÓN DE PAGO ---
const renovarSuscripcion = async (clinica) => {
  const resultado = await Swal.fire({
    title: '¿Confirmar Pago Manual?',
    html: `Al confirmar, se añadirán <b>+30 días</b> al vencimiento de:<br><br><span class="fs-5 fw-bold text-primary">${clinica.nombre_negocio}</span>`,
    icon: 'info',
    showCancelButton: true,
    buttonsStyling: false,
    customClass: {
      confirmButton: 'btn btn-info text-white px-4 mx-2 shadow-sm fw-bold',
      cancelButton: 'btn btn-secondary px-4 mx-2 shadow-sm',
      popup: 'rounded-4 shadow-lg border-0'
    },
    confirmButtonText: 'Sí, registrar pago',
    cancelButtonText: 'Cancelar'
  });

  if (resultado.isConfirmed) {
    try {
      const res = await axios.post(`http://localhost:5000/api/admin/clinicas/${clinica.id}/renovar`);
      cargarClinicas();
      Swal.fire({ title: '¡Suscripción Renovada!', html: `${res.data.mensaje}<br><br>Nueva fecha: <b>${res.data.nueva_fecha}</b>`, icon: 'success', buttonsStyling: false, customClass: { confirmButton: 'btn btn-primary px-4 shadow-sm' } });
    } catch (error) {
      Swal.fire({ title: 'Error', text: error.response?.data?.error || 'No se pudo registrar la renovación.', icon: 'error', buttonsStyling: false, customClass: { confirmButton: 'btn btn-primary px-4 shadow-sm' } });
    }
  }
};

onMounted(() => {
  cargarClinicas();
  cargarPlanes();
  intervaloActualizacion = setInterval(() => { cargarClinicas(); }, 60000);
});

onUnmounted(() => {
  if (intervaloActualizacion) clearInterval(intervaloActualizacion);
});
</script>