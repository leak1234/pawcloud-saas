<template>
  <div class="contenedor">
    <h1>🐾 Bienvenido a PawCloud</h1>
    <p>El sistema SaaS B2B está en línea y Nginx está despachando las pantallas.</p>
    
    <div class="backend-test">
      <h3>Estado del Backend (Flask):</h3>
      <p v-if="loading">Conectando con Flask...</p>
      <p v-else-if="error" style="color: red;">Error: {{ error }}</p>
      <p v-else style="color: green; font-weight: bold;">{{ backendMessage }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const backendMessage = ref('');
const loading = ref(true);
const error = ref('');

onMounted(async () => {
  try {
    // Al probar en local, le pegamos directo al puerto 5000 mapeado en el docker-compose
    const response = await axios.get('http://localhost:5000/api/status');
    backendMessage.value = response.data.message;
  } catch (err) {
    error.value = "No se pudo conectar a PostgreSQL o Flask está apagado.";
    console.error(err);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.contenedor {
  text-align: center;
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.backend-test {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}
</style>