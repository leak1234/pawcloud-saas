<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.6);">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content shadow-lg border-0">
        <div class="modal-header bg-light">
          <h5 class="modal-title fw-bold text-dark">
            {{ editandoId ? '✏️ Editar Clínica' : '➕ Registrar Nueva Clínica' }}
          </h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>

        <form @submit.prevent="guardar">
          <div class="modal-body">
            <div class="caja-seccion mb-3 bg-white p-3 rounded-3 border shadow-sm">
              <h6 class="fw-bold text-primary mb-3">🏢 Datos del Negocio</h6>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold text-secondary small">Nombre del Negocio *</label>
                  <input type="text" class="form-control" v-model="form.nombre_negocio" required maxlength="150" placeholder="Ej: VetCare Sur" />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold text-secondary small">NIT (Opcional)</label>
                  <input type="text" class="form-control" v-model="form.nit" maxlength="50" placeholder="Ej: 1234567018" />
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label fw-semibold text-secondary small">Dirección Física *</label>
                <input type="text" class="form-control" v-model="form.direccion" required maxlength="200" placeholder="Avenida Siempre Viva 123" />
              </div>

              <div class="mb-2">
                <label class="form-label fw-semibold text-secondary small">Plan de Suscripción *</label>
                <select class="form-select border-primary" v-model="form.plan_id" required>
                  <option value="" disabled>-- Selecciona un Plan --</option>
                  <option v-for="plan in planesDisponibles" :key="plan.id" :value="plan.id">
                    {{ plan.nombre }} - ${{ plan.precio }}
                  </option>
                </select>
              </div>
            </div>

            <div class="caja-seccion mb-0 bg-white p-3 rounded-3 border shadow-sm">
              <h6 class="fw-bold text-info mb-3">👤 Cuenta de Administrador Principal</h6>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold text-secondary small">Nombre del Veterinario *</label>
                  <input type="text" class="form-control" v-model="form.nombre_usuario" required maxlength="150" placeholder="Ej: Dr. Juan Pérez" />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label fw-semibold text-secondary small">Correo Electrónico (Acceso) *</label>
                  <input type="email" class="form-control" v-model="form.email" required maxlength="120" placeholder="admin@vetcare.com" />
                </div>
              </div>

              <div class="mb-2">
                <label class="form-label fw-semibold text-secondary small">
                  Contraseña de Acceso <span v-if="editandoId" class="text-warning">(Dejar vacío para no cambiar)</span>
                </label>
                <input type="password" class="form-control" v-model="form.password" :required="!editandoId" maxlength="100" placeholder="Mínimo 6 caracteres" />
              </div>
            </div>
          </div>

          <div class="modal-footer bg-light border-0">
            <button type="button" class="btn btn-secondary fw-bold rounded-pill px-4" @click="$emit('close')">Cancelar</button>
            <button type="submit" class="btn btn-success fw-bold rounded-pill px-4 shadow-sm" :disabled="loading">
              {{ editandoId ? 'Guardar Cambios' : 'Registrar Clínica' }}
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
  clinicaData: Object,
  planesDisponibles: Array
});

const emit = defineEmits(['close', 'guardado']);

const loading = ref(false);
const form = ref({
  nombre_negocio: '', nit: '', direccion: '', nombre_usuario: '', email: '', password: '', plan_id: ''
});

// Sincroniza los datos al abrir el modal
watch(() => props.show, (isOpen) => {
  if (isOpen) {
    if (props.editandoId && props.clinicaData) {
      form.value = {
        nombre_negocio: props.clinicaData.nombre_negocio,
        nit: props.clinicaData.nit === 'S/N' ? '' : props.clinicaData.nit,
        direccion: props.clinicaData.direccion === 'Sin dirección' ? '' : props.clinicaData.direccion,
        nombre_usuario: props.clinicaData.nombre_usuario,
        email: props.clinicaData.email,
        password: '', // Siempre vacío por seguridad
        plan_id: props.clinicaData.plan_id || ''
      };
    } else {
      form.value = { nombre_negocio: '', nit: '', direccion: '', nombre_usuario: '', email: '', password: '', plan_id: '' };
    }
  }
});

const guardar = async () => {
  loading.value = true;
  try {
    const payload = { ...form.value, rol: 'admin' };

    if (props.editandoId) {
      await axios.put(`http://localhost:5000/api/admin/clinicas/${props.editandoId}`, payload);
    } else {
      await axios.post('http://localhost:5000/api/admin/registrar', payload);
    }

    Swal.fire({
      toast: true, position: 'top-end', icon: 'success',
      title: props.editandoId ? 'Clínica actualizada' : 'Clínica registrada',
      showConfirmButton: false, timer: 3000
    });
    
    emit('guardado');
  } catch (error) {
    Swal.fire({
      title: 'Error',
      text: error.response?.data?.error || 'No se pudo procesar la solicitud.',
      icon: 'error', confirmButtonColor: '#0f4c5c'
    });
  } finally {
    loading.value = false;
  }
};
</script>