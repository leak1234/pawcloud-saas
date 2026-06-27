<template>
  <div class="container-fluid">
    <h2 class="mb-4 text-dark fw-bold">Resumen del Sistema</h2>
    
    <!-- 1. TARJETAS DE INDICADORES (KPIs) - Ahora son 4 -->
    <div class="row g-3 mb-4">
      <div class="col-md-6 col-lg-3">
        <div class="card shadow-sm border-0 border-start border-primary border-4 h-100">
          <div class="card-body py-3">
            <h6 class="text-muted mb-2">📊 Total Clínicas</h6>
            <h3 class="fw-bold mb-0 text-dark">{{ cargando ? '...' : estadisticas.total_clinicas }}</h3>
          </div>
        </div>
      </div>

      <div class="col-md-6 col-lg-3">
        <div class="card shadow-sm border-0 border-start border-success border-4 h-100">
          <div class="card-body py-3">
            <h6 class="text-muted mb-2">🟢 Clínicas Activas</h6>
            <h3 class="fw-bold mb-0 text-success">{{ cargando ? '...' : estadisticas.clinicas_activas }}</h3>
          </div>
        </div>
      </div>

      <!-- NUEVA TARJETA: INGRESOS (MRR) -->
      <div class="col-md-6 col-lg-3">
        <div class="card shadow-sm border-0 border-start border-info border-4 h-100" style="background: #f8ffff;">
          <div class="card-body py-3">
            <h6 class="text-muted mb-2">💰 Ingresos Mensuales</h6>
            <h3 class="fw-bold mb-0 text-info">
              {{ cargando ? '...' : '$' + estadisticas.ingresos_mensuales.toFixed(2) }}
            </h3>
          </div>
        </div>
      </div>

      <div class="col-md-6 col-lg-3">
        <div class="card shadow-sm border-0 border-start border-warning border-4 h-100">
          <div class="card-body py-3">
            <h6 class="text-muted mb-2">👥 Usuarios Globales</h6>
            <h3 class="fw-bold mb-0 text-dark">{{ cargando ? '...' : estadisticas.total_usuarios }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. SECCIÓN DE GRÁFICOS -->
    <div class="row g-4 mb-4">
      <!-- NUEVO: GRÁFICO DE CRECIMIENTO (Línea) -->
      <div class="col-lg-8">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-header bg-white border-bottom-0 pt-4 pb-0">
            <h5 class="fw-bold">📈 Crecimiento de Adquisición (Año Actual)</h5>
          </div>
          <div class="card-body position-relative" style="min-height: 250px;">
            <div v-if="cargando" class="text-muted text-center mt-5">Cargando gráfico...</div>
            <Line v-else :data="datosGraficoCrecimiento" :options="opcionesGraficoLinea" />
          </div>
        </div>
      </div>

      <!-- GRÁFICO CIRCULAR DE SUSCRIPCIONES (Anillo) -->
      <div class="col-lg-4">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-header bg-white border-bottom-0 pt-4 pb-0 text-center">
            <h5 class="fw-bold">Estado de Cuentas</h5>
          </div>
          <div class="card-body d-flex justify-content-center align-items-center">
            <div v-if="cargando" class="text-muted">Cargando gráfico...</div>
            <div v-else-if="estadisticas.total_clinicas === 0" class="text-muted">Sin datos</div>
            <div v-else style="width: 100%; max-width: 200px;">
              <Doughnut :data="datosGraficoEstados" :options="opcionesGraficoAnillo" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. TABLAS Y AUDITORÍA -->
    <div class="row g-4">
      <div class="col-lg-8">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-header bg-white border-bottom-0 pt-4 pb-0">
            <h5 class="fw-bold">🕒 Últimas Clínicas Registradas</h5>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-hover align-middle">
                <thead class="table-light">
                  <tr>
                    <th>ID</th>
                    <th>Nombre del Negocio</th>
                    <th>NIT</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="cargando">
                    <td colspan="3" class="text-center py-3 text-muted">Cargando datos...</td>
                  </tr>
                  <tr v-else-if="estadisticas.ultimas_clinicas.length === 0">
                    <td colspan="3" class="text-center py-3 text-muted">No hay clínicas registradas.</td>
                  </tr>
                  <tr v-else v-for="clinica in estadisticas.ultimas_clinicas" :key="clinica.id">
                    <td><span class="badge bg-secondary">#{{ clinica.id }}</span></td>
                    <td class="fw-semibold">{{ clinica.nombre_negocio }}</td>
                    <td>{{ clinica.nit }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- NUEVO: LOG DE ACTIVIDAD RECIENTE -->
      <div class="col-lg-4">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-header bg-white border-bottom-0 pt-4 pb-0">
            <h5 class="fw-bold">📝 Actividad Reciente</h5>
          </div>
          <div class="card-body">
            <div v-if="cargando" class="text-muted text-center">Cargando...</div>
            <div v-else-if="estadisticas.actividad_reciente.length === 0" class="text-muted text-center mt-3">
              No hay actividad reciente.
            </div>
            
            <div v-else class="timeline mt-2">
              <!-- Elemento de la línea de tiempo -->
              <div v-for="(actividad, index) in estadisticas.actividad_reciente" :key="index" class="d-flex mb-3">
                <div class="me-3 fs-5">{{ actividad.icono }}</div>
                <div>
                  <p class="mb-0 small fw-semibold" :class="actividad.color">{{ actividad.mensaje }}</p>
                  <small class="text-muted" style="font-size: 0.75rem;">{{ actividad.fecha }}</small>
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
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

// Importamos Chart.js completo (Incluyendo escalas para gráfico de línea)
import { 
  Chart as ChartJS, ArcElement, Tooltip, Legend,
  CategoryScale, LinearScale, PointElement, LineElement, Title 
} from 'chart.js';
import { Doughnut, Line } from 'vue-chartjs';

// Registramos todos los componentes necesarios de Chart.js
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title);

const estadisticas = ref({
  total_clinicas: 0,
  clinicas_activas: 0,
  clinicas_vencidas: 0,
  clinicas_suspendidas: 0,
  total_usuarios: 0,
  ingresos_mensuales: 0,
  crecimiento_mensual: [],
  actividad_reciente: [],
  ultimas_clinicas: []
});
const cargando = ref(true);

// ---------------- CONFIGURACIÓN GRÁFICO CIRCULAR ----------------
const datosGraficoEstados = computed(() => ({
  labels: ['Activas', 'Vencidas', 'Suspendidas'],
  datasets: [{
    backgroundColor: ['#198754', '#ffc107', '#dc3545'],
    data: [
      estadisticas.value.clinicas_activas,
      estadisticas.value.clinicas_vencidas,
      estadisticas.value.clinicas_suspendidas
    ]
  }]
}));

const opcionesGraficoAnillo = ref({
  responsive: true, maintainAspectRatio: true, cutout: '70%',
  plugins: { legend: { position: 'bottom' } }
});

// ---------------- CONFIGURACIÓN GRÁFICO DE LÍNEA ----------------
const mesesNombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

const datosGraficoCrecimiento = computed(() => ({
  labels: mesesNombres,
  datasets: [{
    label: 'Nuevas Clínicas Registradas',
    backgroundColor: '#0d6efd',
    borderColor: '#0d6efd',
    data: estadisticas.value.crecimiento_mensual,
    tension: 0.4, // Hace que la línea sea curva y suave
    fill: false,
  }]
}));

const opcionesGraficoLinea = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } }, // Ocultamos la leyenda para más limpieza
  scales: {
    y: { beginAtZero: true, ticks: { stepSize: 1 } } // Solo números enteros
  }
});

// ---------------- CARGA DE DATOS ----------------
const cargarEstadisticas = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/admin/estadisticas');
    estadisticas.value = response.data;
  } catch (error) {
    console.error("Error al cargar las estadísticas del dashboard:", error);
  } finally {
    cargando.value = false;
  }
};

onMounted(() => {
  cargarEstadisticas();
});
</script>

<style scoped>
/* Un pequeño toque visual para que la tarjeta del dinero destaque sutilmente */
.border-info { border-color: #0dcaf0 !important; }
.text-info { color: #087990 !important; }
</style>