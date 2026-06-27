<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.6);">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content shadow-lg border-0 rounded-4 overflow-hidden">
        <div class="modal-header bg-white border-bottom-0 pt-4 px-4 pb-2">
          <h4 class="modal-title fw-bold text-dark">{{ modoEdicion ? '✏️ Editar Cliente' : '➕ Registrar Nuevo Cliente' }}</h4>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <form @submit.prevent="guardar">
          <div class="modal-body modal-fondo-gris px-4 py-4">
            <div class="caja-seccion mb-0 bg-white p-4 rounded-3 border">
              <h6 class="fw-bold text-primary mb-3">👤 Datos del Propietario / Cliente</h6>
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label fw-bold text-secondary small mb-1">Nombre Completo *</label>
                  <input type="text" class="form-control" v-model="form.nombre_completo" required maxlength="150" placeholder="Ej: Carlos Mendoza" />
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold text-secondary small mb-1">Teléfono / WhatsApp *</label>
                  <input type="text" class="form-control" v-model="form.telefono" required maxlength="20" @input="form.telefono = form.telefono.replace(/[^0-9]/g, '').slice(0, 20)" placeholder="Solo números" />
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold text-secondary small mb-1">Correo Electrónico</label>
                  <input type="email" class="form-control" v-model="form.email" maxlength="100" placeholder="Opcional" />
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold text-secondary small mb-1">Dirección Física</label>
                  <input type="text" class="form-control" v-model="form.direccion" maxlength="200" placeholder="Opcional" />
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer bg-white border-top-0 px-4 py-3">
            <button type="button" class="btn btn-outline-secondary fw-bold px-4 rounded-pill" @click="$emit('close')">Cancelar</button>
            <button type="submit" class="btn btn-success fw-bold px-4 shadow-sm rounded-pill">Guardar Cliente</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import Swal from 'sweetalert2';

const props = defineProps({
  show: Boolean,
  modoEdicion: Boolean,
  duenoData: Object
});

const emit = defineEmits(['close', 'guardado']);
const clinicaId = sessionStorage.getItem('clinica_id');
const form = ref({ nombre_completo: '', telefono: '', email: '', direccion: '' });

watch(() => props.show, (isOpen) => {
  if (isOpen) {
    form.value = props.modoEdicion && props.duenoData 
      ? { ...props.duenoData, email: props.duenoData.email || '', direccion: props.duenoData.direccion || '' }
      : { nombre_completo: '', telefono: '', email: '', direccion: '' };
  }
});

const guardar = async () => {
  const url = props.modoEdicion 
    ? `http://localhost:5000/api/clinica/${clinicaId}/duenos/${props.duenoData.id}` 
    : `http://localhost:5000/api/clinica/${clinicaId}/duenos`;
  const m = props.modoEdicion ? 'PUT' : 'POST';

  const r = await fetch(url, { method: m, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form.value) });
  if (r.ok) {
    Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Cliente guardado', showConfirmButton: false, timer: 2000 });
    emit('guardado');
  }
};
</script>

<style scoped>
.modal-fondo-gris { background-color: #f4f6f8; }
</style>