<template>
  <div class="container-fluid mt-4">
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        <div class="card shadow-sm border-0 rounded-4 overflow-hidden">
          <div class="card-header bg-dark text-white py-3 px-4">
            <h4 class="mb-0 fw-bold">📲 Vinculación de WhatsApp</h4>
            <p class="text-secondary small mb-0 mt-1">Conecta el número telefónico exclusivo de tu clínica.</p>
          </div>
          <div class="card-body p-5 text-center bg-light">

            <div v-if="loading_inicial" class="py-4">
              <div class="spinner-border text-primary mb-3" role="status"></div>
              <h5 class="fw-bold text-secondary">Verificando conexión actual...</h5>
            </div>

            <div v-else-if="estado === 'CONNECTED'">
              <div class="display-1 text-success mb-3">✅</div>
              <h3 class="fw-bold text-success">¡WhatsApp Sincronizado!</h3>
              <p class="text-secondary">Tu clínica se encuentra enviando expedientes y alertas de forma autónoma.</p>
              <button class="btn btn-outline-danger btn-sm mt-3" @click="confirmarDesvincular">
                <i class="bi bi-trash"></i> Desvincular Teléfono
              </button>
            </div>

            <div v-else-if="estado === 'SCAN_QR'">
              <h4 class="fw-bold text-dark mb-2">Escanea el Código QR</h4>
              <p class="text-secondary small">Abre WhatsApp ➔ Dispositivos vinculados ➔ Escanear</p>
              <div class="bg-white p-3 d-inline-block rounded-3 my-3 shadow-sm border">
                <img :src="qrCode" alt="Código de conexión" style="width: 250px; height: 250px;" />
              </div>
              <div class="d-flex justify-content-center align-items-center gap-2 text-primary small fw-bold">
                <div class="spinner-border spinner-border-sm" role="status"></div>
                <span>Esperando enlace con el móvil...</span>
              </div>
            </div>

            <div v-else>
              <div class="display-1 text-muted mb-3">📵</div>
              <h4 class="fw-bold text-secondary">Sin sincronización activa</h4>
              <p class="text-muted small">Haz clic abajo para generar tu llave de acceso digital.</p>
              <button class="btn btn-primary fw-bold rounded-pill px-5 py-2 mt-3 shadow-sm"
                      :disabled="loading" 
                      @click="obtenerQR">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ loading ? 'Generando código...' : '🔗 Vincular Teléfono' }}
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import Swal from 'sweetalert2';
import { useWhatsapp } from '../composables/useWhatsapp';

const clinicaId = sessionStorage.getItem('clinica_id');
const estado = ref('DISCONNECTED');
const qrCode = ref('');
const loading = ref(false);
const loading_inicial = ref(true);

const { desvincularWhatsapp } = useWhatsapp();

let vigilanteConexion = null;

// Pregunta al servidor si ya estamos conectados
const verificarEstado = async () => {
  try {
    const res = await fetch(`http://localhost:5000/api/whatsapp/instancia/${clinicaId}/estado`);
    if (res.ok) {
      const data = await res.json();
      if (data.status === 'CONNECTED') {
        estado.value = 'CONNECTED';
        // Si ya se conectó, apagamos el vigilante para no saturar el servidor
        if (vigilanteConexion) clearInterval(vigilanteConexion);
      }
    }
  } catch (error) {
    console.error("Error al verificar estado", error);
  } finally {
    loading_inicial.value = false;
  }
};

// Solicitar el QR
const obtenerQR = async () => {
    loading.value = true;
    try {
        const res = await fetch(`http://localhost:5000/api/whatsapp/instancia/${clinicaId}/conectar`, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (res.ok) {
            const data = await res.json();
            if (data.status === 'SCAN_QR') {
                qrCode.value = data.qr;
                estado.value = 'SCAN_QR';
                
                // ENCENDEMOS EL VIGILANTE: Preguntará cada 3 segundos si ya escaneaste
                if (vigilanteConexion) clearInterval(vigilanteConexion);
                vigilanteConexion = setInterval(verificarEstado, 3000);

            } else if (data.status === 'CONNECTED') {
                estado.value = 'CONNECTED';
            }
        }
    } catch (e) {
        Swal.fire('Error', 'No pudimos contactar con el servidor.', 'error');
    } finally {
        loading.value = false;
    }
};

const confirmarDesvincular = async () => {
  const result = await Swal.fire({
    title: '¿Estás seguro?',
    text: "Se cerrará la sesión de WhatsApp.",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Sí, desvincular'
  });

  if (result.isConfirmed) {
    const exito = await desvincularWhatsapp();
    if (exito) {
      estado.value = 'DISCONNECTED';
      qrCode.value = '';
    }
  }
};

// Al entrar a la pantalla, verificamos si ya estábamos conectados antes
onMounted(() => {
  verificarEstado();
});

// Al salir de la pantalla, apagamos el vigilante por seguridad
onUnmounted(() => {
  if (vigilanteConexion) clearInterval(vigilanteConexion);
});
</script>