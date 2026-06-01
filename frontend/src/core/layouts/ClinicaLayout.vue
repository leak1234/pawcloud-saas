<template>
  <div class="d-flex" style="min-height: 100vh; background-color: #f4f7f6;">
    <div class="bg-dark text-white p-3 d-flex flex-column" style="width: 260px; flex-shrink: 0;">
      <h4 class="fw-bold text-center text-warning mb-4 py-2 border-bottom border-secondary">
        🐾 {{ nombreClinica }}
      </h4>
      
      <nav class="nav flex-column gap-1 flex-grow-1">
        <router-link to="/clinica/dashboard" class="nav-link text-white py-2 px-3 rounded">
          <i class="bi bi-speedometer2 me-2"></i> Dashboard
        </router-link>
        <router-link to="/clinica/empleados" class="nav-link text-white py-2 px-3 rounded">
          <i class="bi bi-people me-2"></i> Personal
        </router-link>
        <router-link to="/clinica/clientes" class="nav-link text-white py-2 px-3 rounded">
          <i class="bi bi-person-heart me-2"></i> Clientes y Pacientes
        </router-link>
      </nav>

      <button class="btn btn-outline-danger w-100 mt-auto mt-3 fw-bold" @click="cerrarSesion">
        
        <i class="bi bi-box-arrow-left me-2"></i> Cerrar Sesión
      </button>
    </div>

    <main class="flex-grow-1 p-4">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// CAMBIO: Obtenemos el nombre guardado en el login
const nombreClinica = ref(localStorage.getItem('nombre_clinica') || 'PawCloud Vet');

const cerrarSesion = () => {
  // Limpiamos todo lo relacionado a la sesión actual
  localStorage.removeItem('clinica_id');
  localStorage.removeItem('rol');
  localStorage.removeItem('nombre_clinica');
  router.push('/');
};
</script>

<style scoped>
.router-link-active { 
  background-color: #0d6efd !important; 
  font-weight: bold; 
}

.nav-link:hover { 
  background-color: rgba(255, 255, 255, 0.1); 
  transition: 0.2s; 
}
</style>