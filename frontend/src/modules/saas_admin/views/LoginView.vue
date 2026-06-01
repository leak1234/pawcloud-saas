<template>
  <div class="login-container">
    <div class="login-box">
      <h2>🐾 PawCloud Login</h2>
      <form @submit.prevent="hacerLogin">
        <input type="email" v-model="email" required placeholder="Correo" />
        <input type="password" v-model="password" required placeholder="Contraseña" />
        <button type="submit" :disabled="cargando">Ingresar</button>
      </form>
      <p v-if="mensajeError" style="color:red">{{ mensajeError }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const email = ref('');
const password = ref('');
const cargando = ref(false);
const mensajeError = ref('');

const hacerLogin = async () => {
  cargando.value = true; mensajeError.value = '';
  try {
    const res = await axios.post('http://localhost:5000/api/admin/login', {
      email: email.value, password: password.value
    });
    
    localStorage.setItem('usuario_rol', res.data.rol);
    
    // Desvío basado en el rol
    if (res.data.rol === 'superadmin') {
      router.push('/saas-global');
    } else {
      router.push('/dashboard');
    }
  } catch (error) {
    mensajeError.value = "Credenciales incorrectas.";
  } finally {
    cargando.value = false;
  }
};
</script>

<style scoped>
.login-container { display: flex; justify-content: center; align-items: center; height: 100vh; }
.login-box { background: white; padding: 40px; border-radius: 10px; width: 300px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);}
input { width: 100%; padding: 10px; margin-bottom: 15px; box-sizing: border-box;}
button { width: 100%; padding: 10px; background: #4CAF50; color: white; border: none; cursor: pointer; border-radius: 5px;}
</style>