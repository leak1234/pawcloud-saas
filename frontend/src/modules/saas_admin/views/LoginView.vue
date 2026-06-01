<template>
  <div class="d-flex align-items-center justify-content-center" style="min-height: 100vh; background-color: #f4f6f9;">
    <div class="card shadow-lg border-0" style="width: 400px; border-radius: 15px;">
      <div class="card-body p-5">
        
        <div class="text-center mb-4">
          <h2 class="fw-bold text-primary">🐾 PawCloud</h2>
          <p class="text-muted small">Inicia sesión en tu cuenta</p>
        </div>

        <form @submit.prevent="iniciarSesion">
          <div class="mb-3">
            <label class="form-label fw-bold small text-secondary">Correo Electrónico:</label>
            <input 
              type="email" 
              class="form-control" 
              v-model="credenciales.email" 
              placeholder="ejemplo@correo.com"
              required 
            />
          </div>

          <div class="mb-4">
            <label class="form-label fw-bold small text-secondary">Contraseña:</label>
            <input 
              type="password" 
              class="form-control" 
              v-model="credenciales.password" 
              placeholder="••••••••"
              required 
            />
          </div>

          <button type="submit" class="btn btn-primary w-100 fw-bold shadow-sm mb-3" :disabled="cargando">
            {{ cargando ? 'Ingresando...' : 'Ingresar al Sistema' }}
          </button>

          <div v-if="mensajeError" class="alert alert-danger text-center small p-2 mb-0">
            {{ mensajeError }}
          </div>
        </form>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const credenciales = ref({ email: '', password: '' });
const mensajeError = ref('');
const cargando = ref(false);

const iniciarSesion = async () => {
  mensajeError.value = '';
  cargando.value = true;
  
  try {
    const res = await axios.post('http://localhost:5000/api/admin/login', credenciales.value);
    
    const datosUsuario = res.data;

    // 1. Guardamos la configuración de sesión
    localStorage.setItem('rol', datosUsuario.rol);
    localStorage.setItem('nombre_clinica', datosUsuario.nombre_clinica || 'PawCloud Vet');
    
    if (datosUsuario.clinica_id) {
      localStorage.setItem('clinica_id', datosUsuario.clinica_id);
    }

    // 2. Controlador de Tráfico
    if (datosUsuario.rol === 'superadmin') {
      router.push('/saas-global'); 
    } else if (['admin', 'veterinario', 'cajero', 'peluquero'].includes(datosUsuario.rol)) {
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