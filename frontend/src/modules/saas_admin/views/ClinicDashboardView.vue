<template>
  <div style="padding: 40px; background: #065f46; color: white; height: 100vh;">
    <h1>🐾 Panel Veterinaria</h1>
    <p>Aquí se gestionan las mascotas, inventario y facturas locales.</p>
    <button @click="salir" style="margin-top: 20px; padding: 10px; background: red; color: white; cursor: pointer;">Cerrar Sesión</button>
  </div>
</template>
<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();
const salir = () => { localStorage.clear(); router.push('/'); };
</script>