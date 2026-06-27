<template>
  <div class="d-flex flex-column flex-md-row vh-100 overflow-hidden bg-light">
    
    <header class="d-flex d-md-none justify-content-between align-items-center p-3 text-white shadow-sm z-3" style="background-color: #1e293b;">
      <h5 class="mb-0 fw-bold fs-6">🛠️ PawCloud Admin</h5>
      <button class="btn btn-outline-light btn-sm border-0 fs-4" @click="alternarMenuMovil">☰</button>
    </header>

    <div v-if="menuMovilAbierto" class="position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50 z-2 d-md-none" @click="cerrarMenuMovil"></div>

    <aside class="sidebar d-flex flex-column shadow-lg z-3" style="background-color: #1e293b; color: white;"
           :class="{ 'contraido': sidebarContraido, 'abierto': menuMovilAbierto }">
      
      <div class="p-3 border-bottom border-secondary text-center position-relative d-flex flex-column justify-content-center" style="height: 80px;">
        <div v-if="!sidebarContraido">
          <h2 class="fs-5 fw-bold mb-0">🛠️ PawCloud</h2>
          <span class="badge bg-primary mt-1">Súper Admin</span>
        </div>
        <h2 v-else class="fs-4 mb-0">🛠️</h2>

        <button class="btn btn-primary btn-sm rounded-circle position-absolute d-none d-md-flex align-items-center justify-content-center shadow"
                style="right: -15px; top: 25px; width: 30px; height: 30px;"
                @click="alternarSidebar">
          {{ sidebarContraido ? '▶' : '◀' }}
        </button>
      </div>

      <nav class="nav flex-column flex-grow-1 p-2 gap-1 overflow-auto mt-2">
        <router-link to="/saas-global" class="nav-link text-light rounded d-flex align-items-center item-menu" exact-active-class="activo" @click="cerrarMenuMovil">
          <span class="fs-5">🏠</span>
          <span class="ms-3" v-if="!sidebarContraido">Dashboard</span>
        </router-link>
        
        <router-link to="/saas-global/clinicas" class="nav-link text-light rounded d-flex align-items-center item-menu" active-class="activo" @click="cerrarMenuMovil">
          <span class="fs-5">🏥</span>
          <span class="ms-3" v-if="!sidebarContraido">Clínicas</span>
        </router-link>
        
        <router-link to="/saas-global/planes" class="nav-link text-light rounded d-flex align-items-center item-menu" active-class="activo" @click="cerrarMenuMovil">
          <span class="fs-5">📦</span>
          <span class="ms-3" v-if="!sidebarContraido">Planes</span>
        </router-link>

        <router-link to="/saas-global/reportes" class="nav-link text-light rounded d-flex align-items-center item-menu" active-class="activo" @click="cerrarMenuMovil">
          <span class="fs-5">📄</span>
          <span class="ms-3" v-if="!sidebarContraido">Reportes</span>
        </router-link>

        <router-link to="/saas-global/notificaciones" class="nav-link text-light rounded d-flex align-items-center item-menu" active-class="activo" @click="cerrarMenuMovil">
          <span class="fs-5">📢</span>
          <span class="ms-3" v-if="!sidebarContraido">Avisos del Sistema</span>
        </router-link>
      </nav> 
      
      <div class="p-3 border-top border-secondary mt-auto">
        <button class="btn btn-danger w-100 d-flex align-items-center justify-content-center" @click="cerrarSesion" title="Cerrar Sesión">
          <span class="fs-6">🚪</span> 
          <span class="ms-2 fw-bold" v-if="!sidebarContraido">Salir</span>
        </button>
      </div>
    </aside>

    <main class="flex-grow-1 p-3 p-md-4 overflow-auto">
      <router-view></router-view>
    </main>
    
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const sidebarContraido = ref(false);
const menuMovilAbierto = ref(false);

const alternarSidebar = () => sidebarContraido.value = !sidebarContraido.value;
const alternarMenuMovil = () => menuMovilAbierto.value = !menuMovilAbierto.value;
const cerrarMenuMovil = () => menuMovilAbierto.value = false;

let temporizadorInactividad;
const TIEMPO_LIMITE_MS = 15 * 60 * 1000; // 15 minutos

const cerrarSesion = () => {
  sessionStorage.clear(); 
  router.replace('/'); 
};

const forzarCierrePorInactividad = () => {
  sessionStorage.clear(); 
  router.replace('/?timeout=true'); 
};

const reiniciarTemporizador = () => {
  clearTimeout(temporizadorInactividad);
  temporizadorInactividad = setTimeout(forzarCierrePorInactividad, TIEMPO_LIMITE_MS);
};

onMounted(() => {
  reiniciarTemporizador();
  window.addEventListener('mousemove', reiniciarTemporizador);
  window.addEventListener('keydown', reiniciarTemporizador);
  window.addEventListener('click', reiniciarTemporizador);
  window.addEventListener('scroll', reiniciarTemporizador);
});

onUnmounted(() => {
  clearTimeout(temporizadorInactividad);
  window.removeEventListener('mousemove', reiniciarTemporizador);
  window.removeEventListener('keydown', reiniciarTemporizador);
  window.removeEventListener('click', reiniciarTemporizador);
  window.removeEventListener('scroll', reiniciarTemporizador);
});
</script>

<style scoped>
.sidebar { 
  width: 250px; 
  transition: width 0.3s ease, transform 0.3s ease; 
}
.sidebar.contraido { 
  width: 80px; 
}
.item-menu { transition: 0.2s; }
.item-menu:hover { background-color: rgba(255, 255, 255, 0.1); }
.item-menu.activo { 
  background-color: #3b82f6 !important; 
  font-weight: bold; 
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    height: 100vh;
    left: 0;
    top: 0;
    transform: translateX(-100%);
  }
  .sidebar.abierto {
    transform: translateX(0);
  }
}
</style>