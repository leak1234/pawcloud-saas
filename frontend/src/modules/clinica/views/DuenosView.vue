<template>
  <div class="container-fluid mt-4">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 gap-3">
      <h1 class="text-dark fw-bold fs-3 mb-0">🧑‍🤝‍🧑 Gestión de Clientes y Pacientes</h1>
      <button class="btn btn-primary fw-bold shadow-sm px-4" @click="abrirCrearDueno">+ Nuevo Cliente</button>
    </div>

    <div class="card shadow-sm border-0 mb-3 bg-white rounded-3">
      <div class="card-body py-3">
        <div class="row g-2 align-items-center">
          <div class="col-md-8">
            <div class="input-group">
              <span class="input-group-text bg-light border-secondary-subtle">🔍</span>
              <input type="text" class="form-control bg-light" placeholder="Buscar cliente por nombre o teléfono..." v-model="filtro" />
            </div>
          </div>
          <div class="col-md-4 d-flex justify-content-md-end align-items-center">
            <div class="form-check form-switch mb-0">
              <input class="form-check-input" type="checkbox" role="switch" id="swAct" v-model="verInactivos" @change="cargarDuenos">
              <label class="form-check-label fw-bold text-secondary ms-2" for="swAct" style="cursor: pointer;">
                {{ verInactivos ? '🔴 Suspendidos' : '🟢 Activos' }}
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0 rounded-3 bg-white">
      <div class="card-body p-0 table-responsive">
        <table class="table table-hover table-striped mb-0 align-middle">
          <thead class="table-dark">
            <tr>
              <th class="ps-4 py-3">Cliente (Propietario)</th>
              <th class="py-3">Contacto</th>
              <th class="py-3">Pacientes Asociados (Clic para Ficha)</th>
              <th class="text-center py-3">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="paginados.length === 0"><td colspan="4" class="text-center py-5 text-muted">No se encontraron registros.</td></tr>
            <tr v-for="d in paginados" :key="d.id" :class="{'bg-light opacity-75': verInactivos}">
              <td class="ps-4 fw-bold" :class="verInactivos?'text-secondary text-decoration-line-through':'text-dark'">
                {{ d.nombre_completo }} <div class="text-muted small fw-normal mt-1" v-if="d.direccion">📍 {{ d.direccion }}</div>
              </td>
              
              <td>
                <div class="d-flex align-items-center gap-2">
                  <span class="text-dark fw-semibold small"><i class="bi bi-whatsapp text-success fs-6"></i> {{ d.telefono }}</span>
                  <button class="btn btn-sm btn-success rounded-circle p-0 d-flex align-items-center justify-content-center" 
                          style="width:24px;height:24px;" 
                          :disabled="enviando" 
                          @click="contactarDueno(d)" 
                          title="Enviar mensaje rápido">
                    <span v-if="enviando" class="spinner-border spinner-border-sm" style="width: 12px; height: 12px;"></span>
                    <i v-else class="bi bi-send-fill" style="font-size:0.7rem;"></i>
                  </button>
                </div>
                <div class="text-muted small mt-1" v-if="d.email">✉️ {{ d.email }}</div>
              </td>
              <td>
                <div class="d-flex flex-wrap gap-2 align-items-center">
                  <span v-if="d.mascotas.length===0" class="badge bg-warning-subtle text-warning-emphasis border">Sin pacientes</span>
                  <button v-for="m in d.mascotas" :key="m.id" @click="abrirExpediente(m, d)" class="btn btn-sm text-white rounded-pill px-3 py-1 fw-bold shadow-sm" :class="m.temperamento==='Agresivo'?'btn-danger':m.temperamento==='Nervioso'?'btn-warning text-dark':'btn-info'" style="font-size:0.8rem;">
                    🐾 {{ m.nombre }} <span v-if="m.esterilizado">✂️</span>
                  </button>
                  <button class="btn btn-sm btn-outline-primary rounded-pill px-2 py-1 fw-bold" style="font-size:0.75rem;" @click="abrirAddMascota(d)">➕ Añadir Paciente</button>
                </div>
              </td>
              <td class="text-center">
                <template v-if="!verInactivos">
                  <button class="btn btn-warning btn-sm text-dark fw-bold shadow-sm mx-1" @click="abrirEditarDueno(d)">✏️ Editar</button>
                  <button class="btn btn-danger btn-sm text-white fw-bold shadow-sm mx-1" @click="suspender(d)">Suspender</button>
                </template>
                <template v-else><button class="btn btn-success btn-sm fw-bold shadow-sm" @click="restaurar(d)">♻️ Restaurar</button></template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <ModalDueno :show="mDueno.show" :modo-edicion="mDueno.edit" :dueno-data="mDueno.data" @close="mDueno.show=false" @guardado="alGuardarDueno" />
    <ModalNuevaMascota :show="mMascota.show" :dueno="mMascota.dueno" @close="mMascota.show=false" @guardado="alGuardarMascota" />
    <ModalExpediente :show="mExp.show" :mascota="mExp.mascota" :dueno="mExp.dueno" :servicios-lista="servicios" @close="mExp.show=false" @actualizado="cargarDuenos" @recargar-servicios="cargarServicios" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import Swal from 'sweetalert2';
import ModalDueno from '../components/duenos/ModalDueno.vue';
import ModalNuevaMascota from '../components/duenos/ModalNuevaMascota.vue';
import ModalExpediente from '../components/duenos/ModalExpediente.vue';

// 1. IMPORTAR LA HERRAMIENTA UNIVERSAL DE WHATSAPP
import { useWhatsapp } from '../composables/useWhatsapp';

const duenos = ref([]);
const servicios = ref([]);
const filtro = ref('');
const verInactivos = ref(false);
const pagina = ref(1);
const clinicaId = sessionStorage.getItem('clinica_id');

// 2. INICIALIZAR EL MOTOR DE ENVÍO
const { enviando, enviarMensaje } = useWhatsapp();

// Estados de Modales
const mDueno = ref({ show: false, edit: false, data: null });
const mMascota = ref({ show: false, dueno: null });
const mExp = ref({ show: false, mascota: null, dueno: null });

watch([filtro, verInactivos], () => pagina.value = 1);
const filtrados = computed(() => duenos.value.filter(d => d.nombre_completo.toLowerCase().includes(filtro.value.toLowerCase()) || d.telefono.includes(filtro.value)));
const paginados = computed(() => filtrados.value.slice((pagina.value - 1) * 6, pagina.value * 6));

// 3. NUEVA FUNCIÓN SILENCIOSA DE CONTACTO
const contactarDueno = (dueno) => {
  const texto = `✨ Hola *${dueno.nombre_completo}*. Te saludamos de la clínica veterinaria para recordarte que estamos a tu disposición para el cuidado de tus mascotas.`;
  enviarMensaje(dueno.telefono, texto);
};

const cargarDuenos = async () => {
  const r = await fetch(`http://localhost:5000/api/clinica/${clinicaId}/duenos?estado=${verInactivos.value ? 'inactivos' : 'activos'}`);
  if (r.ok) duenos.value = await r.json();
};
const cargarServicios = async () => {
  const r = await fetch(`http://localhost:5000/api/clinica/${clinicaId}/servicios`);
  if (r.ok) servicios.value = await r.json();
};

const abrirCrearDueno = () => mDueno.value = { show: true, edit: false, data: null };
const abrirEditarDueno = (d) => mDueno.value = { show: true, edit: true, data: d };
const alGuardarDueno = () => { mDueno.value.show = false; cargarDuenos(); };

const abrirAddMascota = (d) => mMascota.value = { show: true, dueno: d };
const alGuardarMascota = () => { mMascota.value.show = false; cargarDuenos(); };

const abrirExpediente = (m, d) => mExp.value = { show: true, mascota: m, dueno: d };

const suspender = async (d) => {
  if ((await Swal.fire({ title: '¿Suspender?', html: `Archivar a <b>${d.nombre_completo}</b>`, icon: 'warning', showCancelButton: true, confirmButtonColor: '#dc3545' })).isConfirmed) {
    await fetch(`http://localhost:5000/api/clinica/${clinicaId}/duenos/${d.id}`, { method: 'DELETE' });
    cargarDuenos();
  }
};
const restaurar = async (d) => {
  if ((await Swal.fire({ title: '¿Restaurar?', html: `Reactivar a <b>${d.nombre_completo}</b>`, icon: 'question', showCancelButton: true, confirmButtonColor: '#198754' })).isConfirmed) {
    await fetch(`http://localhost:5000/api/clinica/${clinicaId}/duenos/${d.id}/restaurar`, { method: 'PATCH' });
    cargarDuenos();
  }
};

onMounted(() => { if (clinicaId) { cargarDuenos(); cargarServicios(); } });
</script>