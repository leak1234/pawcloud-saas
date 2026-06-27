<template>
  <div class="container-fluid vh-100 p-0 overflow-hidden bg-white">
    <div class="row g-0 h-100">

      <!-- PANEL IZQUIERDO -->
      <div class="col-12 col-lg-6 d-none d-lg-flex flex-column justify-content-center align-items-center position-relative panel-izquierdo order-2 order-lg-1">
        
        <div class="decoracion-circulo circulo-1"></div>
        <div class="decoracion-circulo circulo-2"></div>
        
        <div class="z-2 text-center text-white p-5 glass-card" style="max-width: 550px;">
          <h1 class="display-5 fw-bolder mb-4 text-shadow">Gestión Veterinaria<br>en la Nube</h1>
          
          <p class="fs-6 mb-4 opacity-100 fw-light lh-lg px-2 text-light">
            PawCloud es el ecosistema definitivo para clínicas y hospitales. Centraliza <b>historiales clínicos</b>, gestiona citas, controla tu <b>inventario y facturación</b>, y automatiza recordatorios de vacunas. Todo seguro y accesible desde cualquier dispositivo.
          </p>
          
          <div class="d-flex justify-content-center gap-4 mt-4 pt-3 border-top border-secondary border-opacity-50">
            <div class="text-center">
              <div class="icono-feature mb-2 fs-3">☁️</div>
              <span class="small fw-bold">100% Nube</span>
            </div>
            <div class="text-center">
              <div class="icono-feature mb-2 fs-3">🔒</div>
              <span class="small fw-bold">Seguro</span>
            </div>
            <div class="text-center">
              <div class="icono-feature mb-2 fs-3">🩺</div>
              <span class="small fw-bold">Clínico</span>
            </div>
          </div>
        </div>

        <div class="watermark z-1">PawCloud</div>
      </div>

      <!-- PANEL DERECHO LOGIN -->
      <div class="col-12 col-lg-6 d-flex flex-column px-4 py-5 bg-white shadow-lg z-3 position-relative order-1 order-lg-2 overflow-auto">
        
        <div class="m-auto w-100" style="max-width: 420px;">
          
          <div class="mb-5 text-center text-lg-start">
            <h2 class="fw-bold d-flex align-items-center justify-content-center justify-content-lg-start" style="color: #1e293b;">
              <span class="fs-1 me-2">🐾</span> PawCloud
            </h2>
          </div>

          <div class="mb-4 text-center text-lg-start">
            <h3 class="fw-bold text-dark mb-2">Iniciar Sesión</h3>
            <!-- Enlace actualizado a tu WhatsApp en Bolivia -->
            <p class="text-muted small">¿No tienes cuenta? <a href="https://wa.me/59165647973" target="_blank" class="text-decoration-none fw-bold hover-link" style="color: #0f4c5c;">Contactar Soporte</a></p>
          </div>

          <form @submit.prevent="iniciarSesion">
            
            <div v-if="sesionCaducada" class="alert alert-danger rounded small py-2 px-3 mb-4 d-flex align-items-center shadow-sm" style="background-color: #f8d7da; color: #842029; border: none;">
              <span class="fs-5 me-2">⚠️</span> Tiempo de sesión expirado. Por favor, inicia sesión de nuevo.
            </div>
            
            <div class="mb-3">
              <label class="form-label fw-bold text-dark small mb-1">Correo Electrónico</label>
              <input type="email" class="form-control form-control-lg custom-input bg-light" v-model="credenciales.email" placeholder="ejemplo@clinica.com" required />
            </div>

            <div class="mb-3">
              <label class="form-label fw-bold text-dark small mb-1">Contraseña</label>
              <input type="password" class="form-control form-control-lg custom-input bg-light" v-model="credenciales.password" placeholder="••••••••" required />
            </div>

            <!-- "RECORDARME" Seguro (Solo guarda email) -->
            <div class="mb-4 text-start">
              <div class="form-check">
                <input class="form-check-input shadow-none" type="checkbox" id="rememberMe" v-model="recordarEmail">
                <label class="form-check-label text-muted small" for="rememberMe" style="cursor: pointer;">Recordar mi correo</label>
              </div>
            </div>

            <button type="submit" class="btn btn-lg w-100 fw-bold text-white mb-3 btn-login shadow-sm" :disabled="cargando">
              {{ cargando ? 'Verificando...' : 'Ingresar al Sistema' }}
            </button>

            <div v-if="mensajeError" class="alert alert-danger text-center small py-2 px-3 mt-3 border-0 rounded bg-danger bg-opacity-10 text-danger fw-bold fade-in">
              {{ mensajeError }}
            </div>
          </form>

          <div class="mt-5 pt-4 text-center text-muted border-top" style="font-size: 0.8rem;">
            <p class="mb-1">Copyright © 2026 PawCloud SaaS.</p>
            <a href="#" class="text-muted text-decoration-none hover-link">Términos de Servicio</a> | 
            <a href="#" class="text-muted text-decoration-none hover-link">Política de Privacidad</a>
          </div>

        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const route = useRoute(); 

const credenciales = ref({ email: '', password: '' });
const mensajeError = ref('');
const cargando = ref(false);
const sesionCaducada = ref(false);
const recordarEmail = ref(false);

onMounted(() => {
  if (route.query.timeout === 'true') {
    sesionCaducada.value = true;
    router.replace('/');
  }

  // Cargar correo seguro del dominio actual
  const emailGuardado = localStorage.getItem('pawcloud_email_recordado');
  if (emailGuardado) {
    credenciales.value.email = emailGuardado;
    recordarEmail.value = true;
  }
});

const iniciarSesion = async () => {
  mensajeError.value = '';
  cargando.value = true;
  sesionCaducada.value = false; 

  try {
    const res = await axios.post('http://localhost:5000/api/admin/login', credenciales.value);
    const datosUsuario = res.data;

    sessionStorage.setItem('rol', datosUsuario.rol);
    sessionStorage.setItem('nombre_clinica', datosUsuario.nombre_clinica || 'PawCloud Vet');
    
    if (datosUsuario.clinica_id) {
      sessionStorage.setItem('clinica_id', datosUsuario.clinica_id);
    }

    // LÓGICA DE RECORDARME
    if (recordarEmail.value) {
      localStorage.setItem('pawcloud_email_recordado', credenciales.value.email);
    } else {
      localStorage.removeItem('pawcloud_email_recordado');
    }

    if (datosUsuario.rol === 'superadmin') {
      router.push('/saas-global');
    } else if (['admin', 'veterinario', 'recepcionista', 'cajero', 'peluquero'].includes(datosUsuario.rol)) {
      router.push('/clinica/dashboard');
    } else {
      mensajeError.value = 'Rol de usuario no reconocido.';
    }

  } catch (error) {
    mensajeError.value = error.response?.data?.error || 'Error al conectar con el servidor.';
  } finally {
    cargando.value = false;
  }
};
</script>

<style scoped>
.custom-input {
  border: 1px solid #e2e8f0;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  border-radius: 8px;
}
.custom-input:focus {
  border-color: #0f4c5c;
  background-color: #ffffff !important;
  box-shadow: 0 0 0 4px rgba(15, 76, 92, 0.1);
}

.btn-login {
  background-color: #0f4c5c; 
  border: none;
  transition: all 0.3s ease;
  border-radius: 8px;
  letter-spacing: 0.5px;
}
.btn-login:hover {
  background-color: #0b3d4a;
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(15, 76, 92, 0.2) !important;
}

.hover-link:hover {
  color: #0f4c5c !important;
  text-decoration: underline !important;
}

.panel-izquierdo {
  background: linear-gradient(135deg, #1e293b 0%, #0f4c5c 100%);
  overflow: hidden;
}

.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.text-shadow {
  text-shadow: 2px 2px 5px rgba(0,0,0,0.4);
}

.icono-feature {
  width: 55px;
  height: 55px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  transition: transform 0.3s ease, background-color 0.3s ease;
}
.icono-feature:hover {
  transform: translateY(-5px);
  background-color: rgba(255, 255, 255, 0.2);
}

.decoracion-circulo {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0) 100%);
  z-index: 1;
}
.circulo-1 {
  width: 700px;
  height: 700px;
  top: -150px;
  left: -150px;
}
.circulo-2 {
  width: 500px;
  height: 500px;
  bottom: -100px;
  right: -150px;
}

.watermark {
  position: absolute;
  bottom: -4vh;
  left: 50%;
  transform: translateX(-50%);
  font-size: 14vw;
  font-weight: 900;
  color: rgba(255, 255, 255, 0.02);
  white-space: nowrap;
  pointer-events: none;
}

.fade-in {
  animation: fadeIn 0.3s ease-in;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>