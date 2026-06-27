<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.6);">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content shadow-lg border-0 rounded-4 overflow-hidden">
        <div class="modal-header bg-light">
          <h5 class="modal-title fw-bold text-dark">
            {{ editandoId ? '✏️ Editar Plan de Suscripción' : '➕ Registrar Nuevo Plan' }}
          </h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>

        <form @submit.prevent="guardar">
          <div class="modal-body bg-white p-4">
            <div class="caja-seccion border rounded-3 p-3 shadow-sm bg-light">
              <div class="mb-3">
                <label class="form-label fw-bold text-secondary small mb-1">Nombre del Plan *</label>
                <input type="text" class="form-control fw-bold" v-model="form.nombre" required maxlength="50" placeholder="Ej: Básico, Premium..." />
              </div>
              
              <div class="mb-3">
                <label class="form-label fw-bold text-success small mb-1">Precio Mensual ($) *</label>
                <input type="number" step="0.01" min="0" class="form-control border-success text-success fw-bold" v-model="form.precio" required 
                       @keydown="bloquearTeclasNumericasDecimales" placeholder="0.00" />
              </div>

              <div class="row g-3">
                <div class="col-6">
                  <label class="form-label fw-bold text-secondary small mb-1">Límite Veterinarios *</label>
                  <input type="number" min="1" class="form-control" v-model="form.limite_usuarios" required 
                         @keydown="bloquearTeclasNumericasEnteros" placeholder="Ej: 3" />
                </div>
                <div class="col-6">
                  <label class="form-label fw-bold text-secondary small mb-1">Límite Pacientes *</label>
                  <input type="number" min="1" class="form-control" v-model="form.limite_pacientes" required 
                         @keydown="bloquearTeclasNumericasEnteros" placeholder="Ej: 500" />
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer bg-light border-0">
            <button type="button" class="btn btn-outline-secondary fw-bold rounded-pill px-4" @click="$emit('close')">Cancelar</button>
            <button type="submit" class="btn btn-primary fw-bold rounded-pill px-4 shadow-sm" :disabled="loading">
              {{ editandoId ? 'Guardar Cambios' : 'Guardar Plan' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import axios from 'axios';
import Swal from 'sweetalert2';

const props = defineProps({
  show: Boolean,
  editandoId: [Number, String],
  planData: Object
});

const emit = defineEmits(['close', 'guardado']);

const loading = ref(false);
const form = ref({
  nombre: '', precio: '', limite_usuarios: '', limite_pacientes: ''
});

// Sincronizar datos al abrir
watch(() => props.show, (isOpen) => {
  if (isOpen) {
    if (props.editandoId && props.planData) {
      form.value = {
        nombre: props.planData.nombre,
        precio: props.planData.precio,
        limite_usuarios: props.planData.limite_usuarios,
        limite_pacientes: props.planData.limite_pacientes
      };
    } else {
      form.value = { nombre: '', precio: '', limite_usuarios: '', limite_pacientes: '' };
    }
  }
});

// ESCUDOS NUMÉRICOS
const bloquearTeclasNumericasDecimales = (e) => {
  if (['e', 'E', '-', '+'].includes(e.key)) {
    e.preventDefault();
  }
};

const bloquearTeclasNumericasEnteros = (e) => {
  if (['e', 'E', '-', '+', '.', ','].includes(e.key)) {
    e.preventDefault();
  }
};

const guardar = async () => {
  loading.value = true;
  try {
    if (props.editandoId) {
      await axios.put(`http://localhost:5000/api/admin/planes/${props.editandoId}`, form.value);
    } else {
      await axios.post('http://localhost:5000/api/admin/planes', form.value);
    }
    
    Swal.fire({
      toast: true, position: 'top-end', icon: 'success',
      title: props.editandoId ? 'Plan actualizado correctamente' : 'Plan creado con éxito',
      showConfirmButton: false, timer: 2500
    });
    
    emit('guardado');
  } catch (error) {
    Swal.fire({
      title: 'Error',
      text: error.response?.data?.error || 'Hubo un problema al guardar el plan.',
      icon: 'error', buttonsStyling: false, customClass: { confirmButton: 'btn btn-primary px-4 shadow-sm' }
    });
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* Quitar flechas de input number */
input[type=number]::-webkit-inner-spin-button, 
input[type=number]::-webkit-outer-spin-button { 
  -webkit-appearance: none; 
  margin: 0; 
}
input[type=number] {
  -moz-appearance: textfield;
  appearance: textfield;
}
</style>