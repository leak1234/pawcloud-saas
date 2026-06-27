<template>
  <div class="container-fluid mt-4">

    <div class="d-flex justify-content-between align-items-start mb-4">
      <div>
        <div class="d-flex align-items-center gap-3">
          <h1 class="text-dark fw-bold fs-3 mb-1">👋 Bienvenido, Dr(a). {{ nombreUsuario }}</h1>
          <button class="btn btn-sm btn-outline-secondary rounded-pill shadow-sm" @click="cargarDashboard" title="Actualizar datos ahora">
            🔄
          </button>
        </div>
        <p class="text-muted small mb-0">Estatus clínico actual del establecimiento médico veterinario.</p>
      </div>

      <div class="dropdown">
        <button
          class="btn btn-white bg-white border-0 shadow-sm rounded-circle position-relative d-flex align-items-center justify-content-center"
          type="button" data-bs-toggle="dropdown" style="width: 50px; height: 50px; font-size: 1.5rem;">
          🔔
          <span v-if="avisos.length > 0"
            class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger border border-light"
            style="font-size: 0.75rem;">
            {{ avisos.length }}
          </span>
        </button>

        <ul class="dropdown-menu dropdown-menu-end shadow border-0 rounded-4 p-0 mt-2"
          style="width: 350px; max-height: 400px; overflow-y: auto;">
          <li class="p-3 border-bottom bg-light rounded-top-4 d-flex justify-content-between align-items-center">
            <h6 class="mb-0 fw-bold text-dark">Avisos del Sistema</h6>
            <span class="badge bg-primary rounded-pill">{{ avisos.length }} Nuevos</span>
          </li>

          <div v-if="avisos.length === 0" class="p-5 text-center text-muted">📭 <br><small>No hay comunicados
              recientes.</small></div>

          <li v-for="aviso in avisos" :key="aviso.id" class="p-3 border-bottom text-wrap dropdown-item-text"
            style="white-space: normal;">
            <div class="d-flex justify-content-between align-items-center mb-1">
              <span class="badge"
                :class="{ 'bg-info text-dark': aviso.tipo === 'info', 'bg-warning text-dark': aviso.tipo === 'warning', 'bg-danger': aviso.tipo === 'danger' }">
                {{ aviso.tipo === 'info' ? 'ℹ️ Info' : aviso.tipo === 'warning' ? '⚠️ Alerta' : '🚨 Importante' }}
              </span>
              <small class="text-muted" style="font-size: 0.7rem;">{{ aviso.fecha_creacion }}</small>
            </div>
            <h6 class="fw-bold mb-1 mt-2 text-dark fs-6">{{ aviso.titulo }}</h6>
            <p class="mb-0 small text-secondary">{{ aviso.mensaje }}</p>
          </li>
        </ul>
      </div>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-sm-6 col-xl-3" v-for="(kpi, index) in kpiCards" :key="index">
        <div class="card border-0 rounded-4 shadow-sm h-100 p-3 bg-white border-start border-4" :class="kpi.color">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <span class="text-muted small fw-bold text-uppercase">{{ kpi.title }}</span>
              <h2 class="fw-bold text-dark mb-0 mt-1 fs-1">{{ kpi.value }}</h2>
            </div>
            <div class="p-3 rounded-4 fs-3 d-flex align-items-center justify-content-center" :class="kpi.bgIcon"
              style="width: 54px; height: 54px;">
              {{ kpi.icon }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-lg-7 col-xl-8">
        <div class="card border-0 rounded-4 shadow-sm h-100 bg-white overflow-hidden">
          <div class="card-header bg-white py-3 px-4 border-bottom d-flex justify-content-between align-items-center">
            <h5 class="fw-bold text-dark mb-0">📅 Turnos Programados para Hoy</h5>
          </div>
          <div class="card-body p-0 table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light text-secondary small">
                <tr>
                  <th class="ps-4">Hora</th>
                  <th>Paciente</th>
                  <th>Servicio Requerido</th>
                  <th>Contacto Pr.</th>
                  <th class="text-center">Aviso WA</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!stats.citas_hoy || stats.citas_hoy.length === 0">
                  <td colspan="5" class="text-center py-5 text-muted">No se registran turnos previstos para el día de
                    hoy.</td>
                </tr>
                <tr v-for="cita in stats.citas_hoy" :key="cita.id">
                  <td class="ps-4">
                    <div class="fw-bold text-primary fs-5">{{ cita.hora }}</div>
                    <span v-if="cita.retrasada"
                      class="badge bg-danger animate__animated animate__flash animate__infinite mt-1"
                      style="font-size: 0.65rem;">
                      ⚠️ RETRASADA
                    </span>
                    <span v-else class="badge bg-warning text-dark mt-1" style="font-size: 0.65rem;">
                      ⏳ PENDIENTE
                    </span>
                  </td>
                  <td>
                    <div class="fw-bold text-dark">{{ cita.mascota_nombre }}</div>
                    <small class="text-secondary">{{ cita.dueno_nombre }}</small>
                  </td>
                  <td><span class="badge bg-primary bg-opacity-10 text-primary border border-primary px-2 py-1">{{
                      cita.servicio }}</span></td>
                  <td class="text-secondary small">📞 {{ cita.telefono }}</td>
                  <td class="text-center">

                    <button class="btn btn-sm btn-success rounded-circle shadow-sm" style="width: 32px; height: 32px;"
                      :disabled="enviando"
                      @click="enviarMensaje(cita.telefono, `Estimado(a) ${cita.dueno_nombre}, recordamos su cita hoy a las ${cita.hora} para la atención de ${cita.mascota_nombre}.`)"
                      title="Notificar por WhatsApp">
                      <span v-if="enviando" class="spinner-border spinner-border-sm"
                        style="width: 14px; height: 14px;"></span>
                      <i v-else class="bi bi-whatsapp" style="font-size: 0.8rem;"></i>
                    </button>

                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="col-lg-5 col-xl-4">
        <div class="card border-0 rounded-4 shadow-sm h-100 bg-white">
          <div class="card-header bg-white py-3 px-4 border-bottom">
            <h5 class="fw-bold text-dark mb-0">🐾 Últimos Pacientes Ingresados</h5>
          </div>
          <div class="card-body p-3">
            <div v-for="pac in stats.ultimos_pacientes" :key="pac.id"
              class="d-flex align-items-center justify-content-between p-2 border-bottom">
              <div class="d-flex align-items-center gap-3">
                <div class="bg-light p-2 rounded-circle fs-4 text-center" style="width: 44px; height: 44px;">
                  {{ pac.especie === 'Gato' ? '🐱' : pac.especie === 'Ave' ? '🦜' : '🐶' }}
                </div>
                <div>
                  <h6 class="fw-bold text-dark mb-0">{{ pac.nombre }}</h6>
                  <small class="text-muted" style="font-size: 0.75rem;">Prop: {{ pac.dueno }}</small>
                </div>
              </div>
              <span class="badge bg-light text-secondary border">{{ pac.raza }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useWhatsapp } from '../composables/useWhatsapp';

const stats = ref({});
const avisos = ref([]);
const clinicaId = sessionStorage.getItem('clinica_id');
const nombreUsuario = sessionStorage.getItem('nombre_completo') || 'Profesional';

const { enviando, enviarMensaje } = useWhatsapp();

let intervaloAvisos;

const kpiCards = computed(() => [
  { title: 'Citas Hoy', value: stats.value.kpis?.citas_hoy_count || 0, color: 'border-warning', bgIcon: 'bg-warning bg-opacity-10 text-warning', icon: '📅' },
  { title: 'Pacientes Totales', value: stats.value.kpis?.total_mascotas || 0, color: 'border-info', bgIcon: 'bg-info bg-opacity-10 text-info', icon: '🐾' },
  { title: 'Clientes Registrados', value: stats.value.kpis?.total_duenos || 0, color: 'border-primary', bgIcon: 'bg-primary bg-opacity-10 text-primary', icon: '👥' },
  { title: 'Atenciones Mes', value: stats.value.kpis?.consultas_mes || 0, color: 'border-success', bgIcon: 'bg-success bg-opacity-10 text-success', icon: '🩺' }
]);

const cargarDashboard = async () => {
  try {
    const res = await fetch(`http://localhost:5000/api/clinica/${clinicaId}/dashboard`);
    if (res.ok) stats.value = await res.json();
  } catch (error) {
    console.error("Error al cargar dashboard", error);
  }
};

const cargarAvisos = async () => {
  try {
    const res = await fetch(`http://localhost:5000/api/clinicas/avisos-activos`);
    if (res.ok) {
      avisos.value = await res.json();
    }
  } catch (error) {
    console.error("Error al cargar los avisos", error);
  }
};

const actualizarDatosGlobales = () => {
  cargarDashboard();
  cargarAvisos();
};

onMounted(() => {
  if (clinicaId) {
    cargarDashboard();
    cargarAvisos();
    
    // 1. ACTUALIZACIÓN INSTANTÁNEA: Escuchamos el "grito" del Modal
    window.addEventListener('clinica-actualizada', actualizarDatosGlobales);

    // 2. ACTUALIZACIÓN EN SEGUNDO PLANO (cada 10 segundos)
    intervaloAvisos = setInterval(actualizarDatosGlobales, 10000); 
  }
});

onUnmounted(() => {
  // Limpiamos la memoria al salir del Dashboard
  window.removeEventListener('clinica-actualizada', actualizarDatosGlobales);
  if (intervaloAvisos) clearInterval(intervaloAvisos);
});
</script>