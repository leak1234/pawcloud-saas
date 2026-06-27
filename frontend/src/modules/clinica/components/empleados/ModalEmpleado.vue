<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.6);">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content shadow-lg border-0 rounded-4 overflow-hidden">
        <div class="modal-header bg-white border-bottom-0 pt-4 px-4 pb-2">
          <h4 class="modal-title fw-bold text-dark">{{ modoEdicion ? '✏️ Editar Personal' : '➕ Registrar Personal' }}</h4>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <form @submit.prevent="guardar">
          <div class="modal-body modal-fondo-gris px-4 py-4 bg-light">
            <div class="caja-seccion mb-0 bg-white p-4 rounded-3 border shadow-sm">
              <div class="row g-3">
                <div class="col-12">
                  <label class="form-label fw-bold text-secondary small mb-1">Nombre Completo *</label>
                  <input type="text" class="form-control" v-model="form.nombre_completo" required maxlength="150" placeholder="Ej: Dr. Juan Pérez" />
                </div>
                <div class="col-12">
                  <label class="form-label fw-bold text-secondary small mb-1">Correo Electrónico *</label>
                  <input type="email" class="form-control" v-model="form.email" required maxlength="120" placeholder="usuario@clinica.com" />
                </div>
                <div class="col-12">
                  <label class="form-label fw-bold text-secondary small mb-1">Contraseña</label>
                  <input type="password" class="form-control" v-model="form.password" :required="!modoEdicion" maxlength="100" :placeholder="modoEdicion ? 'Dejar en blanco para conservar actual' : 'Mínimo 6 caracteres'" />
                </div>
                <div class="col-12">
                  <label class="form-label fw-bold text-secondary small mb-1">Rol en la Clínica *</label>
                  <select class="form-select fw-bold text-primary" v-model="form.rol" required>
                    <option value="veterinario">🩺 Veterinario (Consultas y recetas)</option>
                    <option value="recepcionista">📅 Recepcionista (Citas y pagos)</option>
                    <option value="cajero">💰 Cajero (Facturación)</option>
                    <option value="peluquero">✂️ Peluquero (Estética animal)</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer bg-white border-top-0 px-4 py-3">
            <button type="button" class="btn btn-outline-secondary fw-bold px-4 rounded-pill" @click="$emit('close')">Cancelar</button>
            <button type="submit" class="btn btn-primary fw-bold px-4 shadow-sm rounded-pill" :disabled="loading">{{ modoEdicion ? 'Guardar Cambios' : 'Registrar Empleado' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import Swal from 'sweetalert2';

const props = defineProps({ show: Boolean, modoEdicion: Boolean, empleadoData: Object });
const emit = defineEmits(['close', 'guardado']);

const clinicaId = sessionStorage.getItem('clinica_id');
const loading = ref(false);
const form = ref({ nombre_completo: '', email: '', password: '', rol: 'veterinario' });

// Sincroniza los datos cuando se abre el modal para editar
watch(() => props.show, (isOpen) => {
  if (isOpen) {
    if (props.modoEdicion && props.empleadoData) {
      form.value = { 
        nombre_completo: props.empleadoData.nombre_completo, 
        email: props.empleadoData.email, 
        password: '', 
        rol: props.empleadoData.rol 
      };
    } else {
      form.value = { nombre_completo: '', email: '', password: '', rol: 'veterinario' };
    }
  }
});

const guardar = async () => {
  loading.value = true;
  try {
    const url = props.modoEdicion 
      ? `http://localhost:5000/api/clinica/${clinicaId}/empleados/${props.empleadoData.id}`
      : `http://localhost:5000/api/clinica/${clinicaId}/empleados`;
    const metodo = props.modoEdicion ? 'PUT' : 'POST';

    const respuesta = await fetch(url, {
      method: metodo,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    });

    if (respuesta.ok) {
      Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: props.modoEdicion ? 'Personal actualizado' : 'Personal registrado', showConfirmButton: false, timer: 3000 });
      emit('guardado');
    } else {
      const errorData = await respuesta.json();
      Swal.fire({ title: 'Error', text: errorData.error || 'Verifica los datos.', icon: 'error', confirmButtonColor: '#0f4c5c' });
    }
  } catch (error) {
    Swal.fire({ title: 'Error', text: 'No se pudo conectar con el servidor.', icon: 'error', confirmButtonColor: '#0f4c5c' });
  } finally {
    loading.value = false;
  }
};
</script>