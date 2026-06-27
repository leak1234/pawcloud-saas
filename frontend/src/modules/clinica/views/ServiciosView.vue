<template>
  <div class="container-fluid mt-4">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 gap-3">
      <h1 class="text-dark fw-bold fs-3 mb-0">🏷️ Tarifario de Servicios Médicos</h1>
      <button class="btn btn-primary fw-bold shadow-sm px-4" @click="abrirModalCrear">+ Nuevo Servicio</button>
    </div>

    <div class="card shadow-sm border-0 mb-3 bg-white rounded-3">
      <div class="card-body py-2 px-4 d-flex justify-content-end align-items-center">
        <div class="form-check form-switch mb-0">
          <input class="form-check-input" type="checkbox" role="switch" id="switchSrvInactivos" v-model="viendoInactivos" @change="cargarServicios">
          <label class="form-check-label fw-bold text-secondary ms-2" for="switchSrvInactivos" style="cursor: pointer;">
            {{ viendoInactivos ? '🔴 Viendo Eliminados (Papelera)' : '🟢 Viendo Activos' }}
          </label>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0 rounded-3 bg-white">
      <div class="card-body p-0 table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-dark">
            <tr>
              <th class="ps-4 py-3">Nombre del Servicio</th>
              <th class="py-3">Precio Base (Bs.)</th>
              <th class="text-center py-3">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="servicios.length === 0">
              <td colspan="3" class="text-center py-5 text-muted">{{ viendoInactivos ? 'No hay servicios en la papelera.' : 'No hay servicios registrados.' }}</td>
            </tr>
            <tr v-for="srv in servicios" :key="srv.id" :class="{'bg-light opacity-75': viendoInactivos}">
              <td class="ps-4 fw-bold" :class="viendoInactivos ? 'text-secondary text-decoration-line-through' : 'text-dark'">{{ srv.nombre }}</td>
              <td class="text-success fw-bold">Bs. {{ srv.precio_base.toFixed(2) }}</td>
              <td class="text-center">
                <template v-if="!viendoInactivos">
                  <button class="btn btn-warning btn-sm fw-bold shadow-sm mx-1 text-dark" @click="prepararEdicion(srv)">✏️ Editar</button>
                  <button class="btn btn-danger btn-sm text-white fw-bold shadow-sm mx-1" @click="eliminarServicio(srv.id, srv.nombre)">🗑️ Eliminar</button>
                </template>
                <template v-else>
                  <button class="btn btn-success btn-sm fw-bold shadow-sm" @click="restaurarServicio(srv.id, srv.nombre)">♻️ Restaurar</button>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="mostrarModal" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.6);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content shadow-lg border-0 rounded-4 overflow-hidden">
          <div class="modal-header bg-white border-bottom-0 pt-4 px-4 pb-2">
            <h4 class="modal-title fw-bold text-dark">{{ modoEdicion ? '✏️ Editar Servicio' : '➕ Nuevo Servicio' }}</h4>
            <button type="button" class="btn-close" @click="mostrarModal = false"></button>
          </div>
          <form @submit.prevent="guardarServicio">
            <div class="modal-body px-4 py-4 bg-light">
              <div class="mb-3">
                <label class="form-label fw-bold text-secondary small mb-1">Nombre del Servicio *</label>
                <input type="text" class="form-control border-secondary-subtle bg-white" v-model="formSrv.nombre" required maxlength="100" placeholder="Ej: Rayos X" />
              </div>
              <div class="mb-3">
                <label class="form-label fw-bold text-success small mb-1">Precio Sugerido (Bs.) *</label>
                <input type="number" step="0.01" min="0" class="form-control border-success bg-white" v-model="formSrv.precio_base" required @keydown="bloquearTeclasNumericas" @input="limitarLongitud($event, 8)" placeholder="0.00" />
              </div>
            </div>
            <div class="modal-footer bg-white border-top-0 px-4 py-3">
              <button type="button" class="btn btn-outline-secondary fw-bold px-4 rounded-pill" @click="mostrarModal = false">Cancelar</button>
              <button type="submit" class="btn btn-primary fw-bold px-4 shadow-sm rounded-pill">Guardar Tarifa</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Swal from 'sweetalert2';

const servicios = ref([]);
const clinicaId = sessionStorage.getItem('clinica_id');
const viendoInactivos = ref(false);
const mostrarModal = ref(false);
const modoEdicion = ref(false);
const idSeleccionado = ref(null);
const formSrv = ref({ nombre: '', precio_base: 0 });

const bloquearTeclasNumericas = (e) => {
  if (['e', 'E', '-', '+'].includes(e.key)) e.preventDefault();
};

const limitarLongitud = (e, maxLength) => {
  if (e.target.value.length > maxLength) e.target.value = e.target.value.slice(0, maxLength);
};

const cargarServicios = async () => {
  const est = viendoInactivos.value ? 'inactivos' : 'activos';
  const res = await fetch(`http://localhost:5000/api/clinica/${clinicaId}/servicios?estado=${est}`);
  if (res.ok) servicios.value = await res.json();
};

const abrirModalCrear = () => {
  modoEdicion.value = false; formSrv.value = { nombre: '', precio_base: '' };
  mostrarModal.value = true;
};

const prepararEdicion = (srv) => {
  modoEdicion.value = true; idSeleccionado.value = srv.id;
  formSrv.value = { nombre: srv.nombre, precio_base: srv.precio_base };
  mostrarModal.value = true;
};

const guardarServicio = async () => {
  const url = modoEdicion.value ? `http://localhost:5000/api/clinica/${clinicaId}/servicios/${idSeleccionado.value}` : `http://localhost:5000/api/clinica/${clinicaId}/servicios`;
  const m = modoEdicion.value ? 'PUT' : 'POST';
  const res = await fetch(url, { method: m, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formSrv.value) });
  if (res.ok) {
    Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Tarifario guardado', showConfirmButton: false, timer: 2000 });
    mostrarModal.value = false; cargarServicios();
  }
};

const eliminarServicio = async (id, nombre) => {
  const result = await Swal.fire({ title: '¿Eliminar Servicio?', html: `¿Enviar <b>${nombre}</b> a la papelera?`, icon: 'warning', showCancelButton: true, confirmButtonColor: '#dc3545', confirmButtonText: 'Eliminar', reverseButtons: true });
  if (result.isConfirmed) {
    await fetch(`http://localhost:5000/api/clinica/${clinicaId}/servicios/${id}`, { method: 'DELETE' });
    cargarServicios();
  }
};

const restaurarServicio = async (id, nombre) => {
  const result = await Swal.fire({ title: '¿Restaurar Servicio?', html: `¿Reactivar <b>${nombre}</b>?`, icon: 'question', showCancelButton: true, confirmButtonColor: '#198754', confirmButtonText: 'Restaurar', reverseButtons: true });
  if (result.isConfirmed) {
    await fetch(`http://localhost:5000/api/clinica/${clinicaId}/servicios/${id}/restaurar`, { method: 'PATCH' });
    cargarServicios();
  }
};

onMounted(() => { if (clinicaId) cargarServicios(); });
</script>

<style scoped>
.input-enfocado:focus { background-color: #ffffff; border-color: #0d6efd; box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.15); }
input[type=number]::-webkit-inner-spin-button, input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
input[type=number] { -moz-appearance: textfield; appearance: textfield; }
</style>