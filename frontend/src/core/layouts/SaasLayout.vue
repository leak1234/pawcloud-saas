<template>
  <div class="layout-admin">
    <aside class="sidebar">
      <div class="logo-container">
        <h2>🛠️ PawCloud Admin</h2>
        <p class="rol-badge">Súper Administrador</p>
      </div>

      <nav class="menu">
        <router-link to="/saas-global" exact-active-class="activo">🏠 Dashboard</router-link>
        <router-link to="/saas-global/clinicas" active-class="activo">🏥 Clínicas</router-link>
      </nav>

      <div class="sidebar-footer">
        <button class="btn-salir" @click="cerrarSesion">Cerrar Sesión</button>
      </div>
    </aside>

    <main class="contenido-principal">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();

const cerrarSesion = () => {
  localStorage.clear();
  router.push('/');
};
</script>

<style scoped>
.layout-admin { display: flex; height: 100vh; background-color: #f1f5f9; }
.sidebar { width: 260px; background-color: #1e293b; color: white; display: flex; flex-direction: column; }
.logo-container { padding: 20px; border-bottom: 1px solid #334155; text-align: center; }
.rol-badge { font-size: 12px; background: #3b82f6; padding: 4px 8px; border-radius: 12px; display: inline-block; margin-top: 5px; }
.menu { flex-grow: 1; padding: 20px 0; display: flex; flex-direction: column; gap: 5px; }
.menu a { text-decoration: none; color: #cbd5e1; padding: 15px 20px; transition: 0.2s; font-size: 16px;}
.menu a:hover, .menu a.activo { background-color: #334155; color: white; border-left: 4px solid #3b82f6; }
.sidebar-footer { padding: 20px; border-top: 1px solid #334155; }
.btn-salir { width: 100%; padding: 10px; background: #ef4444; color: white; border: none; border-radius: 5px; cursor: pointer; }
.contenido-principal { flex-grow: 1; padding: 40px; overflow-y: auto; }
</style>